# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Michael Viriyananda
#    2016
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
    'name': 'Base Copy User Access',
    'version': '8.0.1.0.0',
    'author': 'Michael Viriyananda,Odoo Community Association (OCA)',
    'category': 'Generic Modules/Base',
    'description': """
        This module represent another function of Access Right from Odoo
        Basic Module.
        The customize is create a wizard
        to copy access right from another user.
    """,
    'website': 'http://github.com/mikevhe18',
    'images': [],
    'depends': ['base'],
    'data': ['wizards/wizard_base_copyUserAccess.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
