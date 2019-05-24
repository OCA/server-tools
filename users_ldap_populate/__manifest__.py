# -*- coding: utf-8 -*-
# Copyright 2012-2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "LDAP Populate",
    "version": "10.0.3.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Authentication",
    "depends": [
        'auth_ldap',
        'users_ldap_menu',
    ],
    'external_dependencies': {
        'python': ['ldap'],
    },
    "data": [
        'data/ir_cron.xml',
        'views/res_company_ldap.xml',
        'wizards/populate_wizard.xml',
    ],
    'installable': True,
}
