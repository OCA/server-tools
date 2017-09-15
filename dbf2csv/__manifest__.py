# -*- coding: utf-8 -*-
# Copyright 2017 INGETIVE (<https://ingetive.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Convert DBF to CSV',
    'version': '10.0.1.0.0',
    'author': 'Félix Villafranca (Ingetive),'
              'Odoo Community Association (OCA)',
    'website': 'http://www.ingetive.com',
    'license': 'AGPL-3',
    'category': 'Usability',
    'contributors': [
        'Félix Villafranca <f.villafranca@ingetive.com>',
    ],
    'summary': "Convert DBF file to CSV file",
    'depends': [
        'base',
    ],
    'data': [
        'wizard/dbf2csv.xml',
    ],
    "demo": [
    ],
    'external_dependencies': {
        'python': ['dbfpy'],
    },
    'auto_install': False,
    'installable': True,
    'application': False,
}
