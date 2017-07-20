# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Module Auto Update',
    'summary': 'Automatically update Odoo modules',
    'version': '10.0.1.0.0',
    'category': 'Extra Tools',
    'website': 'https://odoo-community.org/',
    'author': 'LasLabs, '
              'Juan José Scarafía, '
              'Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'external_dependencies': {
        'python': [
            'checksumdir',
        ],
    },
    'depends': [
        'base',
    ],
    'data': [
        'views/module_views.xml',
        'data/cron_data.xml',
    ],
}
