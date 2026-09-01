# Copyright 2026 Ledoent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    @api.constrains("sentry_client_cdn_base")
    def _check_sentry_client_cdn_base(self):
        for rec in self:
            url = rec.sentry_client_cdn_base or ""
            if url and not (
                url.startswith("/")
                or url.startswith("http://")
                or url.startswith("https://")
            ):
                raise ValidationError(
                    self.env._(
                        "Sentry SDK source URL must start with '/', 'http://', "
                        "or 'https://'. Got: %(url)s",
                        url=url,
                    )
                )

    @api.constrains("sentry_client_browser_dsn")
    def _check_sentry_client_browser_dsn(self):
        for rec in self:
            dsn = (rec.sentry_client_browser_dsn or "").strip()
            if not dsn:
                continue
            # Sentry DSNs look like https://<public_key>@<host>[:port]/<project_id>
            # Public DSNs are safe to embed in client code per Sentry's docs;
            # we still validate shape to fail fast on typos.
            if not (dsn.startswith("http://") or dsn.startswith("https://")):
                raise ValidationError(
                    self.env._(
                        "Sentry Browser DSN must start with 'http://' or "
                        "'https://'. Got: %(dsn)s",
                        dsn=dsn,
                    )
                )
            if "@" not in dsn or "/" not in dsn.split("@", 1)[1]:
                raise ValidationError(
                    self.env._(
                        "Sentry Browser DSN must be of the form "
                        "https://<public_key>@<host>/<project_id>. "
                        "Got: %(dsn)s",
                        dsn=dsn,
                    )
                )

    # Connection — DSN and tag overrides. All three are optional; when blank,
    # the controller falls back to the [sentry] section of odoo.conf so a
    # single-project deployment shared with the OCA `sentry` server-side
    # module keeps working without UI clicks.
    sentry_client_browser_dsn = fields.Char(
        string="Browser DSN",
        config_parameter="sentry_client.browser_dsn",
        help="Public Sentry DSN for the browser project. Leave blank to "
        "reuse the DSN from the [sentry] section of odoo.conf. Sentry "
        "recommends a separate project per platform (Python vs. "
        "JavaScript-Browser); set this to that project's DSN. Browser "
        "DSNs are public by design and safe to expose to end users.",
    )
    sentry_client_environment = fields.Char(
        string="Environment tag",
        config_parameter="sentry_client.environment",
        help="Tags every browser event with this environment "
        "(e.g. 'production-web', 'staging-web'). Leave blank to inherit "
        "from the [sentry] section of odoo.conf.",
    )
    sentry_client_release = fields.Char(
        string="Release tag",
        config_parameter="sentry_client.release",
        help="Tags every browser event with this release identifier "
        "(e.g. the asset-bundle hash or a deploy SHA). Leave blank to "
        "inherit from the [sentry] section of odoo.conf.",
    )

    # Tier 0 — always-free essentials
    sentry_client_enabled = fields.Boolean(
        string="Enable browser error reporting",
        config_parameter="sentry_client.enabled",
        help="When enabled and a DSN is configured (either above or in the "
        "[sentry] section of odoo.conf), the Sentry browser SDK is loaded "
        "into the Odoo web client and captures uncaught JS errors and "
        "unhandled promise rejections.",
    )
    sentry_client_cdn_base = fields.Char(
        string="Sentry SDK source URL",
        config_parameter="sentry_client.cdn_base",
        default="/sentry_client/static/lib/sentry",
        help="Where the Sentry browser SDK bundle is loaded from. Defaults "
        "to the bundle vendored inside this module so no external network "
        "call is needed. Override to point at a mirror or back at the "
        "public CDN at https://browser.sentry-cdn.com.",
    )
    sentry_client_cdn_version = fields.Char(
        string="Sentry SDK version",
        config_parameter="sentry_client.cdn_version",
        default="10.53.1",
    )

    # Tier 1 — performance monitoring
    sentry_client_tier1_tracing_enabled = fields.Boolean(
        string="Enable performance monitoring (Tier 1)",
        config_parameter="sentry_client.tier1_tracing_enabled",
    )
    sentry_client_tier1_traces_sample_rate = fields.Float(
        string="Traces sample rate",
        config_parameter="sentry_client.tier1_traces_sample_rate",
        default=0.0,
        help="Fraction of requests to record performance traces for. "
        "0.0 = none, 1.0 = all. Recommended in production: 0.05 or below.",
    )
    sentry_client_tier1_warning = fields.Char(
        compute="_compute_sentry_client_tier1_warning"
    )

    # Tier 2 — session replay
    sentry_client_tier2_replay_enabled = fields.Boolean(
        string="Enable session replay (Tier 2)",
        config_parameter="sentry_client.tier2_replay_enabled",
    )
    sentry_client_tier2_session_sample_rate = fields.Float(
        string="Healthy-session sample rate",
        config_parameter="sentry_client.tier2_session_sample_rate",
        default=0.0,
        help="Fraction of HEALTHY user sessions to record. Keep at 0.0 "
        "unless you have a specific UX debugging need.",
    )
    sentry_client_tier2_error_sample_rate = fields.Float(
        string="On-error session sample rate",
        config_parameter="sentry_client.tier2_error_sample_rate",
        default=1.0,
        help="Fraction of sessions that hit an error to record. 1.0 means "
        "every errored session is captured for replay.",
    )
    sentry_client_tier2_warning = fields.Char(
        compute="_compute_sentry_client_tier2_warning"
    )

    # Tier 3 — niche extras
    sentry_client_tier3_feedback_enabled = fields.Boolean(
        string="Enable user feedback widget",
        config_parameter="sentry_client.tier3_feedback_enabled",
    )
    sentry_client_tier3_profiling_enabled = fields.Boolean(
        string="Enable browser CPU profiling",
        config_parameter="sentry_client.tier3_profiling_enabled",
        help="Captures JS Self-Profiling samples for traced transactions. "
        "Requires the page to be served with a "
        "`Document-Policy: js-profiling` HTTP header — without it the "
        "integration registers but never collects samples. See CONFIGURE.",
    )
    sentry_client_tier3_profiles_sample_rate = fields.Float(
        string="Profiles sample rate",
        config_parameter="sentry_client.tier3_profiles_sample_rate",
        default=0.0,
        help="Fraction of traced transactions for which to also capture a "
        "browser CPU profile. 0.0 = none, 1.0 = all. Recommended in "
        "production: 0.05 or below.",
    )
    sentry_client_tier3_logs_enabled = fields.Boolean(
        string="Capture console logs",
        config_parameter="sentry_client.tier3_logs_enabled",
    )
    sentry_client_tier3_profiling_warning = fields.Char(
        compute="_compute_sentry_client_tier3_profiling_warning"
    )

    @api.depends("sentry_client_tier1_tracing_enabled")
    def _compute_sentry_client_tier1_warning(self):
        for rec in self:
            if rec.sentry_client_tier1_tracing_enabled:
                rec.sentry_client_tier1_warning = self.env._(
                    "Adds roughly 5–10%% per-request overhead at sample rate 1.0 "
                    "and instruments every fetch/XHR. Recommended in production: "
                    "0.05 or below. In development, 1.0 is fine."
                )
            else:
                rec.sentry_client_tier1_warning = False

    @api.depends("sentry_client_tier2_replay_enabled")
    def _compute_sentry_client_tier2_warning(self):
        for rec in self:
            if rec.sentry_client_tier2_replay_enabled:
                rec.sentry_client_tier2_warning = self.env._(
                    "Adds ~100KB to every page and records DOM mutations + console "
                    "+ network activity. Keep Healthy-session sample at 0.0 and "
                    "On-error sample at 1.0 so recording only kicks in for sessions "
                    "that already broke."
                )
            else:
                rec.sentry_client_tier2_warning = False

    @api.depends(
        "sentry_client_tier1_tracing_enabled",
        "sentry_client_tier3_profiling_enabled",
    )
    def _compute_sentry_client_tier3_profiling_warning(self):
        for rec in self:
            if (
                rec.sentry_client_tier3_profiling_enabled
                and not rec.sentry_client_tier1_tracing_enabled
            ):
                rec.sentry_client_tier3_profiling_warning = self.env._(
                    "Browser CPU profiling is enabled but Tier 1 tracing is OFF. "
                    "Profiles only attach to traced transactions — with tracing off, "
                    "no profiles will be collected. Enable Tier 1 to use profiling."
                )
            else:
                rec.sentry_client_tier3_profiling_warning = False
