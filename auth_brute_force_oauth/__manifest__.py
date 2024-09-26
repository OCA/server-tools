# -*- coding: utf-8 -*-
# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Authentification - Brute-Force Filter (Oauth Support)',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'author': "Quartile Limited, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/server-tools',
    'license': 'AGPL-3',
    'depends': [
        "auth_oauth",
        "auth_brute_force",
    ],
    'data': [],
    'installable': True,
    'auto_install': True,
}
