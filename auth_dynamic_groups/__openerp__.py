# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013-2015 Therp BV (<http://therp.nl>).
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
    "name": "Dynamic groups",
    "version": "8.0.1.0.0",
    "author": "Therp BV",
    "license": "AGPL-3",
    "complexity": "normal",
    'summary': 'Have membership conditions for certain groups',
    "category": "Tools",
    "depends": [
        'base',
    ],
    "data": [
        'view/res_groups.xml',
    ],
    "auto_install": False,
    "installable": True,
    "external_dependencies": {
        'python': [],
    },
}
