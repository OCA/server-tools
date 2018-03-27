# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Module Auto Update',
    'summary': 'Automatically update Odoo modules',
    'version': '9.0.2.0.1',
    'category': 'Extra Tools',
    'website': 'https://github.com/OCA/server-tools',
    'author': 'LasLabs, '
              'Juan José Scarafía, '
              'Tecnativa, '
              'ACSONE SA/NV, '
              'Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'uninstall_hook': 'uninstall_hook',
    'depends': [
        'base',
    ],
    'data': [
        'data/cron_data_deprecated.xml',
    ],
}
