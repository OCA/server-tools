# Copyright 2017 ACSONE SA/NV
# Copyright 2024 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Import Default Enable Tracking",
    "summary": """
        This modules simply enables history tracking when doing an import.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "maintainers": [
        "benwillig",
    ],
    "website": "https://github.com/OCA/server-tools",
    "depends": [
        "base_import",
    ],
    "assets": {
        "web.assets_backend": [
            "/base_import_default_enable_tracking/static/src/xml/base_import.xml"
        ]
    },
}
