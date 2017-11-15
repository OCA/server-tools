# -*- coding: utf-8 -*-
#
#    Author: Oleksandr Paziuk
#    Copyright 2017 Camptocamp SA
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

{
    'name': 'POS configuration with server_environment',
    'version': '9.0.1.0.0',
    'category': 'Tools',
    'summary': 'Configure POS hardware with server_environment_files',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'http://odoo-community.org',
    'depends': [
        'point_of_sale',
        'server_environment',
        'server_environment_files',
    ],
    'data': [
        'views/pos_view.xml',
    ],
    'installable': True,
    'active': False,
}
