# Copyright 2025 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Database Size",
    "version": "18.0.1.0.2",
    "author": "Opener B.V.,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base_setup"],
    "license": "AGPL-3",
    "category": "Tools",
    "data": [
        "data/ir_cron_data.xml",
        "security/ir.model.access.csv",
        "views/ir_model_size_views.xml",
        "views/res_config_settings_views.xml",
        "report/ir_model_size_report_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "database_size/static/src/scss/list_view_wrap_header.scss",
        ]
    },
    "installable": True,
}
