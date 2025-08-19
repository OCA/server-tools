# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Export Html Text",
    "version": "16.0.1.0.0",
    "website": "https://github.com/OCA/server-tools",
    "author": "Quartile, Odoo Community Association (OCA)",
    "category": "Tools",
    "license": "AGPL-3",
    "depends": ["base"],
    "assets": {
        "web.assets_backend": [
            "export_html_text/static/src/js/*.esm.js",
            "export_html_text/static/src/xml/*.xml",
        ],
    },
    "installable": True,
}
