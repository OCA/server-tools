# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Module Checksum Upgrade',
    'summary': 'Base mechanism to detect changes to '
               'installed Odoo modules and upgrade them '
               'automatically',
    'version': '9.0.1.0.0',
    'category': 'Extra Tools',
    'website': 'https://github.com/OCA/server-tools/',
    'author': 'ACSONE SA/NV, '
              'LasLabs, '
              'Juan José Scarafía, '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [
            'checksumdir',
        ],
    },
    'depends': [
        'base',
    ],
}
