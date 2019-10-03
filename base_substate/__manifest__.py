# Copyright 2019 Akretion (<http://www.akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Sub State",
    "version": "12.0.1.0.0",
    "category": "Tools",
    "author": "Akretion, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow/",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        'security/base_substate_security.xml',
        'security/ir.model.access.csv',
        "views/base_substate_views.xml",
    ],
    "installable": True,
}
