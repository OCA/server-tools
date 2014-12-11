# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Daniel Reis (https://launchpad.com/~dreis-pt)
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
    'name': "LDAP mapping for user name and e-mail",
    'version': "1.0",
    'depends': ["auth_ldap"],
    'author': "Daniel Reis (https://launchpad.com/~dreis-pt)",
    'description': """\
Allows to define the LDAP attributes to use to retrieve user name and e-mail
address.

The default attribute used for the name is "cn".
For Active Directory, you might prefer to use "displayName" instead.
AD also supports the "mail" attribute, so it can be mapped into OpenERP.
""",
    'category': "Tools",
    'data': [
        'users_ldap_view.xml',
    ],
    'installable': True,
}
