# Copyright 2022 Camptocamp SA, Trobz
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Base model for Selection field",
    "summary": "Store values in db for more flexible selections",
    "version": "15.0.1.0.0",
    "author": "Trobz, Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": ["base"],
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "views/base_selection_view.xml",
    ],
}
