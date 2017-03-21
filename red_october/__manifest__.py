# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Red October',
    'version': '10.0.1.0.0',
    'category': 'Security',
    'author': "LasLabs, "
              "Odoo Community Association (OCA)",
    'website': 'https://laslabs.com',
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': [
            'red_october',
        ],
    },
    'data': [
        'views/assets.xml',
        'views/red_october_delegation.xml',
        'views/red_october_file.xml',
        'views/red_october_user.xml',
        'views/red_october_vault.xml',
        'views/red_october_menu.xml',
        'wizards/red_october_vault_activate.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
}
