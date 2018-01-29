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
    "name": "Groups assignment",
    "version": "8.0.1.2.1",
    "depends": ["auth_ldap"],
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "summary": """
Adds user accounts to groups based on rules defined by the administrator.
""",
    "category": "Tools",
    "data": [
        'users_ldap_groups.xml',
        'security/ir.model.access.csv',
    ],
    "installable": False,
    "external_dependencies": {
        'python': ['ldap'],
    },
}
