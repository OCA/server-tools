# Copyright (C) 2026 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Read auditlog records stored in clickhouse.",
    "version": "18.0.1.0.0",
    "summary": "Read auditlog from clickhouse using FDW",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA), Cetmix",
    "website": "https://github.com/OCA/server-tools",
    "depends": [
        "auditlog_clickhouse_write",
    ],
    "data": [
        "views/auditlog_clickhouse_config_views.xml",
    ],
}
