# -*- coding: utf-8 -*-
##############################################################################
#
#    Adapted by Nicolas Bessi. Copyright Camptocamp SA
#    Based on Florent Xicluna original code. Copyright Wingo SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Example server configuration environment files repository module",
    "version": "1.0",
    "depends": ["base"],
    "author": "Camptocamp",
    "description": """\
File store for environment file sample module
=============================================

This module provides a file store for classical configuration by
environment file pattern into OpenERP provided by the
`server_environment` addon.  Please look at this module for more info
and doc.

Note: you should not install this module 'as is', since it is an
example module, but rather adapt it to your needs, and ensure your
version of the module gets picked up by OpenERP. This can be ensured
by putting the directory where your version of
server_environment_files lives before this one in the addons-path
variable of the OpenERP configuration file.
    """,
    "website": "http://www.camptocamp.com",
    "category": "Tools",
    "data": [],
    "installable": True,
    "active": False,
}
