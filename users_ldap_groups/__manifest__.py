# -*- coding: utf-8 -*-
# Copyright 2012-2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "LDAP groups assignment",
    "version": "10.0.1.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "summary": "Adds users to Odoo groups based on groups in LDAP.",
    "category": "Authentication",
    "depends": [
        'auth_ldap',
        'users_ldap_menu',
    ],
    "data": [
        'views/res_company_ldap.xml',
        'security/ir.model.access.csv',
    ],
    "external_dependencies": {
        'python': ['ldap'],
    },
}
