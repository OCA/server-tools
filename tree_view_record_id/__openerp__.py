# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2012-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
#     @author David BEAL <david.beal@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Tree View Record Id',
    'version': '0.1',
    'category': 'Other modules',
    'sequence': 10,
    'author': 'Akretion',
    'summary': "Adds id field to tree views",
    'description': """
Adds Id field to all non arborescent tree views.
Id field is the primary key of the table (Odoo model).
Arborescent views like 'Products by Category' or 'Chart of accounts' haven't this field included.
    """,
    'website': 'http://www.akretion.com',
    'depends': [
        'base',
    ],
    'data': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [
    ],
    'css': [
    ],
    'js': [
    ],
    'qweb': [
    ],
}
