# Copyright 2026 Ledoent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import http
from odoo.http import request
from odoo.tools import config as odoo_config

_logger = logging.getLogger(__name__)

# The keys the server-side OCA `sentry` module reads on the 18.0 series:
# plain options in odoo.conf's [options] section (the dedicated [sentry]
# section only exists from 19.0).
_SENTRY_CONF_KEYS = ("sentry_dsn", "sentry_environment", "sentry_release")


def _read_sentry_config():
    """Read the server-side `sentry_*` options from the Odoo configuration.

    Used as a fallback when the browser DSN / release / environment are NOT
    set via `ir.config_parameter`; this keeps a single-project deployment
    working out of the box when the same DSN is shared with the server-side
    OCA `sentry` module, which on 18.0 is configured with top-level
    `sentry_*` options in odoo.conf.
    """
    return {
        key: odoo_config.get(key) for key in _SENTRY_CONF_KEYS if odoo_config.get(key)
    }


def _bundle_name(tracing, replay, feedback):
    """Compose the Sentry browser SDK bundle filename for a given tier mix.

    Sentry's CDN ships `bundle.{tracing,replay,feedback}.min.js` but does NOT
    ship `bundle.tracing.feedback.min.js` — when tracing+feedback are both on
    without replay, we fall back to the tracing+replay+feedback bundle. The
    extra replay code is inert without our integration registering it, so the
    only cost is bandwidth.
    """
    if feedback and tracing and not replay:
        replay = True
    parts = ["bundle"]
    if tracing or replay:
        parts.append("tracing")
    if replay:
        parts.append("replay")
    if feedback:
        parts.append("feedback")
    return ".".join(parts) + ".min.js"


class SentryClientController(http.Controller):
    @http.route(
        "/sentry_client/config.json",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
        sitemap=False,
    )
    def config(self, **kwargs):
        """Return the runtime config for the browser SDK.

        Public on purpose — portal users and the login page need it before
        authentication. The DSN is a public DSN; only behaviour flags and the
        authenticated user's *numeric* id leave the server here. Email + name
        come from `window.odoo.session_info` on the client side, which is
        already gated by the session cookie.
        """
        params = request.env["ir.config_parameter"].sudo()
        get = params.get_param

        def _bool(key):
            return get(key, "False") == "True"

        def _rate(key, default="0.0"):
            try:
                return max(0.0, min(1.0, float(get(key, default))))
            except (TypeError, ValueError):
                return float(default)

        if not _bool("sentry_client.enabled"):
            return request.make_json_response({"enabled": False})

        # DSN / environment / release resolution order:
        #   1. `ir.config_parameter` (UI-settable, per-database)
        #   2. `sentry_*` options in odoo.conf (server-admin, the same keys
        #      the OCA `sentry` server-side module reads on 18.0)
        # The two paths exist so platform-split deployments can give the
        # browser its own Sentry project (Sentry's recommended setup — JS
        # platform separate from the Python platform) while single-project
        # deployments still work without UI clicks.
        sentry_conf = _read_sentry_config()

        def _resolve(icp_key, conf_key):
            return get(icp_key) or sentry_conf.get(conf_key) or None

        dsn = _resolve("sentry_client.browser_dsn", "sentry_dsn")
        if not dsn:
            return request.make_json_response({"enabled": False})

        tracing = _bool("sentry_client.tier1_tracing_enabled")
        replay = _bool("sentry_client.tier2_replay_enabled")
        feedback = _bool("sentry_client.tier3_feedback_enabled")
        profiling = _bool("sentry_client.tier3_profiling_enabled")
        logs = _bool("sentry_client.tier3_logs_enabled")

        cdn_base = get(
            "sentry_client.cdn_base", "/sentry_client/static/lib/sentry"
        ).rstrip("/")
        cdn_version = get("sentry_client.cdn_version", "10.53.1")
        bundle_url = (
            f"{cdn_base}/{cdn_version}/{_bundle_name(tracing, replay, feedback)}"
        )
        profiling_addon_url = (
            f"{cdn_base}/{cdn_version}/browserprofiling.min.js" if profiling else None
        )

        payload = {
            "enabled": True,
            "dsn": dsn,
            "release": _resolve("sentry_client.release", "sentry_release"),
            "environment": _resolve("sentry_client.environment", "sentry_environment"),
            "bundle_url": bundle_url,
            "profiling_addon_url": profiling_addon_url,
            "integrations": {
                "tracing": tracing,
                "replay": replay,
                "feedback": feedback,
                "profiling": profiling,
                "logs": logs,
            },
            "traces_sample_rate": _rate("sentry_client.tier1_traces_sample_rate"),
            "replay_session_sample_rate": _rate(
                "sentry_client.tier2_session_sample_rate"
            ),
            "replay_error_sample_rate": _rate(
                "sentry_client.tier2_error_sample_rate", "1.0"
            ),
            "profiles_sample_rate": _rate("sentry_client.tier3_profiles_sample_rate"),
        }

        user = request.env.user
        if user and not user._is_public():
            payload["user_id"] = user.id
            if replay:
                payload["replay_optout"] = bool(user.sentry_client_replay_optout)
            # Ship role primitives so the browser SDK can tag every event
            # with the user's groups + app categories. Downstream training
            # corpora bucket sessions by these tags to keep "sales rep"
            # behaviour separate from "accountant" behaviour. Group full
            # names ("Sales / Salesperson") are easier to grok than xmlids
            # in Sentry tag-search.
            all_groups = user.sudo().groups_id
            payload["groups"] = all_groups.mapped("full_name") or all_groups.mapped(
                "name"
            )
            payload["categories"] = sorted(
                {
                    cat.name
                    for cat in all_groups.mapped("category_id")
                    if cat and cat.name
                }
            )

        return request.make_json_response(payload)
