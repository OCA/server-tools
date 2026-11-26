# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Data Import Log from Filesystem",
    "summary": "Pick import files up from a filesystem storage and log them",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "author": "Quartile, Odoo Community Association (OCA)",
    "maintainers": ["AungKoKoLin1997"],
    "website": "https://github.com/OCA/server-tools",
    "license": "LGPL-3",
    "depends": ["data_import_log", "fs_storage"],
    "data": [
        "security/ir.model.access.csv",
        "views/data_import_pickup_views.xml",
        "views/data_import_log_views.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
}
