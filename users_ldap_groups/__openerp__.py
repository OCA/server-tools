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
    "version": "1.2",
    "depends": ["auth_ldap"],
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "description": """
Adds user accounts to groups based on rules defined by the administrator.

Usage:

Define mappings in Settings->Companies->[your company]->tab configuration->[your
ldap server].

Decide whether you want only groups mapped from ldap (Only ldap groups=y) or a
mix of manually set groups and ldap groups (Only ldap groups=n). Setting this to
'no' will result in users never losing privileges when you remove them from a
ldap group, so that's a potential security issue. It is still the default to
prevent losing group information by accident.

For active directory, use LDAP attribute 'memberOf' and operator 'contains'.
Fill in the DN of the windows group as value and choose an OpenERP group users
with this windows group are to be assigned to.

For posix accounts, use operator 'query' and a value like
(&(cn=bzr)(objectClass=posixGroup)(memberUid=$uid))

The operator query matches if the filter in value returns something, and value
can contain $[attribute] which will be replaced by the first value of the
user's ldap record's attribute named [attribute].
""",
    "category": "Tools",
    "data": [
        'users_ldap_groups.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "external_dependencies": {
        'python': ['ldap'],
    },
}
