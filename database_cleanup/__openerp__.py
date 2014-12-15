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
    'name': 'Database cleanup',
    'version': '0.1',
    'author': 'Therp BV',
    'depends': ['base'],
    'license': 'AGPL-3',
    'category': 'Tools',
    'data': [
        'view/purge_modules.xml',
        'view/purge_models.xml',
        'view/purge_columns.xml',
        'view/purge_tables.xml',
        'view/purge_data.xml',
        'view/menu.xml',
        ],
}
