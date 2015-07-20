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
    'author': "Akretion,Odoo Community Association (OCA)",
    'summary': "Adds id field to tree views",
    'description': """
Adds Id field in all tree views of any modules/models, except:

* Arborescent tree views like 'Products by Category', 'Chart of accounts', etc.
* Tree views (like in wizard 'Change password') built on transient models
  which don't have this column in their table.

Id field is the primary key of standard sql tables
defined by the orm (Odoo model).
    """,
    'website': 'http://www.akretion.com',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
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
