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
    "name": "Authenticate via HTTP basic authentication",
    "version": "1.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "complexity": "expert",
    "description": """
In an environment where several web applications authenticate against the same
source, the simplest way to attain single sign on would be to have the
webserver handle authentication and pass the login information via HTTP headers
to the application it proxies.

This addon allows for this setup. Technically, it picks up the HTTP
Authorization header, extracts a username and a password and tries to login
into the first database found in the database list.

If you have to set a specific database, possibly depending on the login
provided, use the addon dbfilter_from_header.

The addon has to be loaded as server-wide module.


Funders:

Open2bizz software & consultancy
    """,
    "category": "",
    "depends": [
    ],
    "data": [
    ],
    "js": [
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
