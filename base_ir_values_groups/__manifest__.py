# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Add groups on ir.values',
    'version': '10.0.1.0.0',
    'category': 'Server tools',
    'summary': 'Add groups on ir.values to hide them.',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA), '
              'ACSONE SA/NV',
    'maintainer': 'Odoo Community Association (OCA)',
    'website': 'http://odoo-community.org',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir_values.xml',
        'views/ir_values.xml',
    ],
}
