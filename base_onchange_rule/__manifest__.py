# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base Onchange Rules",
    "summary": "Define onchange settings for any models",
    "version": "10.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://odoo-community.org/",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        'base',
    ],
    "post_init_hook": "post_init_hook",
    "data": [
        'security/ir.model.access.csv',
        'views/onchange_rule_view.xml',
    ],
    "demo": [
        'demo/partner_demo.xml',
    ],
    "installable": True,
}
