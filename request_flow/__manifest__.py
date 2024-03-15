# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Request Flow",
    "version": "14.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "summary": "Create and validate request_flow",
    "depends": ["mail", "hr", "product"],
    "data": [
        "security/request_security.xml",
        "security/ir.model.access.csv",
        "data/mail_data.xml",
        "views/request_category_views.xml",
        "views/request_product_line_views.xml",
        "views/request_views.xml",
        "views/res_users_views.xml",
    ],
    "demo": [
        "demo/request_category_data.xml",
    ],
    "maintainers": ["kittiu"],
    "application": True,
    "installable": True,
}
