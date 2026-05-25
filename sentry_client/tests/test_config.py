# Copyright 2026 Ledoent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import tempfile
import textwrap
from unittest.mock import patch

from odoo.tests import HttpCase, tagged

from ..controllers.main import _bundle_name, _read_sentry_section


@tagged("post_install", "-at_install")
class TestBundleName(HttpCase):
    def test_tier0_only(self):
        self.assertEqual(_bundle_name(False, False, False), "bundle.min.js")

    def test_tracing_only(self):
        self.assertEqual(_bundle_name(True, False, False), "bundle.tracing.min.js")

    def test_replay_only_falls_back_to_tracing_replay(self):
        # Sentry's CDN doesn't ship `bundle.replay.min.js` for the tier
        # combinations this module exposes — replay-only piggybacks on the
        # tracing+replay bundle. The integration list still controls what
        # runs; the extra tracing code is inert without the integration.
        self.assertEqual(
            _bundle_name(False, True, False), "bundle.tracing.replay.min.js"
        )

    def test_feedback_only(self):
        self.assertEqual(_bundle_name(False, False, True), "bundle.feedback.min.js")

    def test_tracing_plus_feedback_falls_back_to_full_bundle(self):
        # Sentry's CDN doesn't ship `bundle.tracing.feedback.min.js`.
        self.assertEqual(
            _bundle_name(True, False, True),
            "bundle.tracing.replay.feedback.min.js",
        )

    def test_all_three(self):
        self.assertEqual(
            _bundle_name(True, True, True),
            "bundle.tracing.replay.feedback.min.js",
        )


@tagged("post_install", "-at_install")
class TestReadSentrySection(HttpCase):
    def test_returns_empty_when_no_config_path(self):
        with patch("odoo.addons.sentry_client.controllers.main.odoo_config") as cfg:
            cfg.get.return_value = None
            self.assertEqual(_read_sentry_section(), {})

    def test_returns_empty_when_conf_has_no_sentry_section(self):
        with tempfile.NamedTemporaryFile("w", suffix=".conf", delete=False) as fh:
            fh.write("[options]\ndb_host = localhost\n")
            path = fh.name
        with patch("odoo.addons.sentry_client.controllers.main.odoo_config") as cfg:
            cfg.get.return_value = path
            self.assertEqual(_read_sentry_section(), {})

    def test_reads_sentry_section_from_odoo_conf(self):
        with tempfile.NamedTemporaryFile("w", suffix=".conf", delete=False) as fh:
            fh.write(
                textwrap.dedent(
                    """\
                    [options]
                    db_host = localhost
                    [sentry]
                    sentry_dsn = https://abc@example.com/1
                    sentry_release = 1.2.3
                    """
                )
            )
            path = fh.name
        with patch("odoo.addons.sentry_client.controllers.main.odoo_config") as cfg:
            cfg.get.return_value = path
            section = _read_sentry_section()
        self.assertEqual(section.get("sentry_dsn"), "https://abc@example.com/1")
        self.assertEqual(section.get("sentry_release"), "1.2.3")


@tagged("post_install", "-at_install")
class TestConfigEndpoint(HttpCase):
    def setUp(self):
        super().setUp()
        self.params = self.env["ir.config_parameter"].sudo()

    def _set(self, key, value):
        self.params.set_param(key, value)

    def _get_config(self):
        resp = self.url_open("/sentry_client/config.json")
        self.assertEqual(resp.status_code, 200)
        return json.loads(resp.content)

    def test_disabled_when_master_off(self):
        self._set("sentry_client.enabled", "False")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertEqual(payload, {"enabled": False})

    def test_disabled_when_dsn_missing(self):
        self._set("sentry_client.enabled", "True")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={},
        ):
            payload = self._get_config()
        self.assertEqual(payload, {"enabled": False})

    def test_tier0_only_bundle(self):
        self._set("sentry_client.enabled", "True")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertTrue(payload["enabled"])
        self.assertTrue(payload["bundle_url"].endswith("/bundle.min.js"))
        self.assertFalse(payload["integrations"]["tracing"])
        self.assertFalse(payload["integrations"]["replay"])

    def test_tier1_bundle_and_sample_rate(self):
        self._set("sentry_client.enabled", "True")
        self._set("sentry_client.tier1_tracing_enabled", "True")
        self._set("sentry_client.tier1_traces_sample_rate", "0.05")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertIn(".tracing", payload["bundle_url"])
        self.assertNotIn(".replay", payload["bundle_url"])
        self.assertEqual(payload["traces_sample_rate"], 0.05)

    def test_tier2_bundle_and_replay_rates(self):
        self._set("sentry_client.enabled", "True")
        self._set("sentry_client.tier2_replay_enabled", "True")
        self._set("sentry_client.tier2_session_sample_rate", "0.0")
        self._set("sentry_client.tier2_error_sample_rate", "1.0")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertIn(".tracing.replay", payload["bundle_url"])
        self.assertEqual(payload["replay_session_sample_rate"], 0.0)
        self.assertEqual(payload["replay_error_sample_rate"], 1.0)

    def test_all_tiers_bundle(self):
        self._set("sentry_client.enabled", "True")
        self._set("sentry_client.tier1_tracing_enabled", "True")
        self._set("sentry_client.tier2_replay_enabled", "True")
        self._set("sentry_client.tier3_feedback_enabled", "True")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertTrue(
            payload["bundle_url"].endswith("/bundle.tracing.replay.feedback.min.js")
        )

    def test_anonymous_payload_omits_user_keys(self):
        self._set("sentry_client.enabled", "True")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertNotIn("user_id", payload)
        self.assertNotIn("replay_optout", payload)

    def test_authenticated_payload_includes_user_id_no_email(self):
        # The public endpoint must NOT leak email — only the numeric uid.
        # The JS reads email + name from window.odoo.session_info on the client.
        self._set("sentry_client.enabled", "True")
        self.authenticate("admin", "admin")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertEqual(payload["user_id"], self.env.ref("base.user_admin").id)
        self.assertNotIn("email", json.dumps(payload).lower())

    def test_authenticated_payload_includes_groups_and_categories(self):
        # Browser SDK tags every event with the user's role primitives so
        # downstream training corpora can bucket sessions by app category.
        self._set("sentry_client.enabled", "True")
        self.authenticate("admin", "admin")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertIsInstance(payload.get("groups"), list)
        self.assertTrue(payload["groups"], "admin should have at least one group")
        self.assertIsInstance(payload.get("categories"), list)

    def test_bundle_url_defaults_to_vendored_path(self):
        self._set("sentry_client.enabled", "True")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertIn("/sentry_client/static/lib/sentry/", payload["bundle_url"])
        self.assertNotIn("browser.sentry-cdn.com", payload["bundle_url"])

    def test_profiling_payload_includes_addon_url(self):
        self._set("sentry_client.enabled", "True")
        self._set("sentry_client.tier1_tracing_enabled", "True")
        self._set("sentry_client.tier3_profiling_enabled", "True")
        self._set("sentry_client.tier3_profiles_sample_rate", "0.1")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertTrue(payload["integrations"]["profiling"])
        self.assertEqual(payload["profiles_sample_rate"], 0.1)
        self.assertTrue(payload["bundle_url"].endswith("/bundle.tracing.min.js"))
        self.assertTrue(
            payload["profiling_addon_url"].endswith("/browserprofiling.min.js")
        )

    def test_profiling_addon_absent_when_off(self):
        self._set("sentry_client.enabled", "True")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertIsNone(payload["profiling_addon_url"])

    def test_sample_rates_clamped(self):
        self._set("sentry_client.enabled", "True")
        self._set("sentry_client.tier1_traces_sample_rate", "2.5")  # > 1.0
        self._set("sentry_client.tier2_session_sample_rate", "-0.5")  # < 0.0
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertEqual(payload["traces_sample_rate"], 1.0)
        self.assertEqual(payload["replay_session_sample_rate"], 0.0)

    def test_browser_dsn_from_ir_config_parameter_wins_over_conf(self):
        # UI-set DSN must take precedence over the odoo.conf fallback. This
        # is the platform-split case: backend Python project on the conf
        # DSN, browser JS project on the UI DSN.
        self._set("sentry_client.enabled", "True")
        self._set("sentry_client.browser_dsn", "https://browser@example.com/2")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://backend@example.com/1"},
        ):
            payload = self._get_config()
        self.assertEqual(payload["dsn"], "https://browser@example.com/2")

    def test_browser_dsn_falls_back_to_odoo_conf(self):
        # Single-project deployment: no UI DSN, conf DSN is used.
        self._set("sentry_client.enabled", "True")
        self._set("sentry_client.browser_dsn", "")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://backend@example.com/1"},
        ):
            payload = self._get_config()
        self.assertEqual(payload["dsn"], "https://backend@example.com/1")

    def test_environment_and_release_from_ir_config_parameter_win(self):
        self._set("sentry_client.enabled", "True")
        self._set("sentry_client.browser_dsn", "https://x@example.com/1")
        self._set("sentry_client.environment", "production-web")
        self._set("sentry_client.release", "asset-bundle-deadbeef")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={
                "sentry_environment": "production",
                "sentry_release": "1.3.2",
            },
        ):
            payload = self._get_config()
        self.assertEqual(payload["environment"], "production-web")
        self.assertEqual(payload["release"], "asset-bundle-deadbeef")

    def test_environment_and_release_fall_back_to_odoo_conf(self):
        self._set("sentry_client.enabled", "True")
        self._set("sentry_client.browser_dsn", "https://x@example.com/1")
        self._set("sentry_client.environment", "")
        self._set("sentry_client.release", "")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={
                "sentry_dsn": "https://x@example.com/1",
                "sentry_environment": "production",
                "sentry_release": "1.3.2",
            },
        ):
            payload = self._get_config()
        self.assertEqual(payload["environment"], "production")
        self.assertEqual(payload["release"], "1.3.2")

    def test_browser_dsn_validation_rejects_malformed(self):
        from odoo.exceptions import ValidationError

        settings = self.env["res.config.settings"].create({})
        with self.assertRaises(ValidationError):
            settings.sentry_client_browser_dsn = "not-a-url"
            settings._check_sentry_client_browser_dsn()
        with self.assertRaises(ValidationError):
            settings.sentry_client_browser_dsn = "https://example.com/1"
            settings._check_sentry_client_browser_dsn()

    def test_browser_dsn_validation_accepts_valid(self):
        settings = self.env["res.config.settings"].create({})
        settings.sentry_client_browser_dsn = "https://abc123@sentry.example.com/42"
        settings._check_sentry_client_browser_dsn()  # no raise

    def test_replay_optout_only_when_replay_on(self):
        self._set("sentry_client.enabled", "True")
        self.authenticate("admin", "admin")
        admin = self.env.ref("base.user_admin")
        admin.sentry_client_replay_optout = True
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            # Replay tier off → no replay_optout in payload at all
            payload = self._get_config()
        self.assertNotIn("replay_optout", payload)
        # Replay tier on → opt-out surfaces
        self._set("sentry_client.tier2_replay_enabled", "True")
        with patch(
            "odoo.addons.sentry_client.controllers.main._read_sentry_section",
            return_value={"sentry_dsn": "https://x@example.com/1"},
        ):
            payload = self._get_config()
        self.assertTrue(payload["replay_optout"])
        admin.sentry_client_replay_optout = False
