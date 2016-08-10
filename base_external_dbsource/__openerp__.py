# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis, 2011
#    Additional contributions by Maxime Chambreuil, Savoir-faire Linux
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
    'name': 'External Database Sources',
    'version': '9.0.1.0.0',
    'category': 'Tools',
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': 'http://launchpad.net/addons-tko',
    'license': 'AGPL-3',
    'images': [
        'images/screenshot01.png',
    ],
    'depends': [
        'base',
    ],
    'data': [
        'views/base_external_dbsource.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/base_external_dbsource.xml',
    ],
    'installable': True,
}
