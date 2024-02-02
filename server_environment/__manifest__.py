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
    "name": "server configuration environment files",
    "version": "10.0.1.3.0",
    "depends": ["base"],
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "summary": "move some configurations out of the database",
    "website": "https://github.com/OCA/server-tools"
               "/tree/10.0/server_environment",
    "license": "GPL-3 or any later version",
    "category": "Tools",
    "preloadable": False,
    "data": [
        'security/res_groups.xml',
        'serv_config.xml',
    ],
    'installable': True,
}
