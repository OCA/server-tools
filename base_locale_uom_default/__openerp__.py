# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Locale - Default UoM',
    'summary': 'This provides settings to select default UoMs at the '
               'language level.',
    'version': '9.0.1.0.0',
    'category': 'Extra Tools',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs, '
              'Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'product',
    ],
    'data': [
        'views/res_lang_view.xml',
    ],
    'demo': [
        'demo/res_lang_demo.xml',
    ],
}
