# -*- coding: utf-8 -*-
# Copyright © 2014-2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Fields Validator",
    'version': '8.0.1.0.0',
    'category': 'Tools',
    'summary': "Validate fields using regular expressions",
    'author': 'Agile Business Group, Odoo Community Association (OCA)',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": ['base'],
    "data": [
        'views/ir_model_view.xml',
        'security/ir.model.access.csv',
        'data/ir_model_regex_data.xml',
        ],
    "demo": [
        'demo/ir_model_regex_demo.yml',
        ],
    'test': [
        'test/validator.yml',
    ],
    "active": False,
    "installable": False,
}
