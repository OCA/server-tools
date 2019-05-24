# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "LDAP menu",
    "version": "10.0.0.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "summary": "Adds menu entry for easy access to LDAP settings",
    "category": "Authentication",
    "depends": [
        "auth_ldap",
    ],
    "data": [
        'views/res_company_ldap.xml',
        'views/menu.xml',
    ],
}
