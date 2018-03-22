# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Module Auto Update',
    'summary': 'Automatically update Odoo modules',
    'version': '8.0.2.0.0',
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
    'install_hook': 'install_hook',
    'uninstall_hook': 'uninstall_hook',
    'depends': [
        'base',
    ],
}
