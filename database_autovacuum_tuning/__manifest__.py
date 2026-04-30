# Copyright 2026 Camptocamp (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

{
    "name": "Database Autovacuum Tuning",
    "summary": "Scheduled checks for Odoo autovacuum thresholds and scale factors",
    "version": "18.0.1.0.1",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": [
        "base_setup",
    ],
    "data": [
        "data/config_parameter.xml",
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/database_autovacuum_tuning_views.xml",
    ],
    "development_status": "Alpha",
    "license": "LGPL-3",
    "installable": True,
}
