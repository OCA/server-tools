# Copyright 2020-2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Data Import Log",
    "summary": "Log models for unattended data imports, with per-record errors",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "author": "Quartile, Odoo Community Association (OCA)",
    "maintainers": ["AungKoKoLin1997"],
    "website": "https://github.com/OCA/server-tools",
    "license": "LGPL-3",
    "depends": ["mail", "queue_job"],
    "external_dependencies": {"python": ["openpyxl"]},
    "data": [
        "security/data_import_security.xml",
        "security/ir.model.access.csv",
        "views/data_import_log_views.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
}
