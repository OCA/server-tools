# -*- coding: utf-8 -*-
# Copyright Daniel Reis (https://launchpad.com/~dreis-pt).
# Copyright 2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/gpl.html).
{
    'name': "LDAP mapping for user name and e-mail",
    'version': "10.0.2.0.0",
    'author': "Daniel Reis (https://launchpad.com/~dreis-pt),"
              "Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    "category": "Authentication",
    "depends": [
        'auth_ldap',
        'users_ldap_menu',
    ],
    'data': [
        'views/res_company_ldap.xml',
    ],
    'installable': True,
}
