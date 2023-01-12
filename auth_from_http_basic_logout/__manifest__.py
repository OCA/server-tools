# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
    "name": "Authenticate via HTTP basic authentication (logout helper)",
    "version": "1.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "complexity": "expert",
    "description": """
With auth_from_http_basic, the logout procedure has to be bent a bit to provide
a good user experience. As the former has to be a server wide module, this is
the clientside complement which provides the javascript part.

The addon has to be installed in the database in use.


Funders:

Open2bizz software & consultancy
    """,
    "category": "",
    "depends": [
        'web',
        'auth_from_http_basic',
    ],
    "data": [
    ],
    "js": [
        'static/src/js/auth_from_http_basic_logout.js',
    ],
    "css": [
    ],
    "qweb": [
    ],
    "auto_install": False,
    "installable": False,
    "external_dependencies": {
        'python': [],
    },
}
