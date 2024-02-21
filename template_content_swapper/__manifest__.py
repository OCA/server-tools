# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Template Content Swapper",
    "version": "16.0.1.0.0",
    "author": "Quartile Limited, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/template_content_mapping_views.xml",
    ],
    "installable": True,
}
