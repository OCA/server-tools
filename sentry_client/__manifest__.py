# Copyright 2026 Ledoent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sentry — Browser SDK",
    "summary": "Capture Odoo web-client JS errors in Sentry, "
    "with tiered opt-in for tracing and session replay",
    "version": "19.0.1.0.0",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Ledoent, Odoo Community Association (OCA)",
    "maintainers": ["dnplkndll"],
    "license": "AGPL-3",
    "depends": ["web"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/res_users_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sentry_client/static/src/js/sentry_loader.js",
            "sentry_client/static/src/js/owl_error_boundary.esm.js",
            "sentry_client/static/src/js/feedback_systray.esm.js",
            "sentry_client/static/src/xml/feedback_systray.xml",
        ],
        "web.assets_frontend": [
            "sentry_client/static/src/js/sentry_loader.js",
        ],
    },
    "installable": True,
    "application": False,
}
