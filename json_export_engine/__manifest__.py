# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "JSON Export Engine",
    "summary": (
        "Universal JSON schema builder, REST API, webhooks and" " scheduled exports"
    ),
    "version": "18.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "kobros-tech, Odoo Community Association (OCA)",
    "maintainers": ["kobros-tech"],
    "license": "AGPL-3",
    "development_status": "Alpha",
    "external_dependencies": {
        "python": ["requests"],
    },
    "depends": [
        "base",
        "web",
        "jsonifier",
    ],
    "data": [
        "security/json_export_engine_security.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/json_export_schema_views.xml",
        "views/json_export_endpoint_views.xml",
        "views/json_export_webhook_views.xml",
        "views/json_export_schedule_views.xml",
        "views/json_export_log_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "json_export_engine/static/src/json_export_widget.xml",
            "json_export_engine/static/src/json_export_widget.esm.js",
        ],
    },
    "demo": [
        "demo/json_export_demo.xml",
        "demo/ir.exports.line.csv",
    ],
    "installable": True,
}
