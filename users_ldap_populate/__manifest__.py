# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "LDAP Populate",
    "version": "10.0.1.0.0",
    "author": (
        "Therp BV",
        "Odoo Community Association (OCA)",
    ),
    "license": "AGPL-3",
    "category": 'Tools',
    "description": """
This module allows to prepopulate the user database with all entries in the
LDAP database.

In order to schedule the population of the user database on a regular basis,
create a new scheduled action with the following properties:

- Object: res.company.ldap
- Function: action_populate
- Arguments: [res.company.ldap.id]

Substitute res.company.ldap.id with the actual id of the res.company.ldap
object you want to query.
""",
    "depends": [
        'auth_ldap',
    ],
    'external_dependencies': {
        'python': ['ldap'],
    },
    "data": [
        'views/users_ldap.xml',
        'views/populate_wizard.xml',
    ],
    'installable': True,
}
