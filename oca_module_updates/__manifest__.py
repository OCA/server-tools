# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Oca Module Updates",
    "summary": """
        Get OCA Module updates""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": [
        "mail",
    ],
    "external_dependencies": {"python": ["feedparser", "packaging"]},
    "data": [
        "security/oca_update_security.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/oca_update_tag.xml",
        "views/oca_update_module.xml",
        "views/oca_update_version.xml",
        "data/ir_cron.xml",
        "data/version_data.xml",
    ],
}
