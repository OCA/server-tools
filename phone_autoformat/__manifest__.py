# Copyright 2026 Syed Sameed Zafar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Phone Auto Format",
    "summary": "Automatically format phone numbers on save and in forms",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Syed Sameed Zafar, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["base", "phone_validation"],
    "external_dependencies": {"python": ["phonenumbers"]},
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
