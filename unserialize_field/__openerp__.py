# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>)
#    All Rights Reserved
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
    'name': 'Make database fields from fields that live in serialized fields',
    'version': '1.0',
    'description': """To be able to search for fields with standard methods,
they have to be database fields. This addon makes it possible to unserialize
them afterwards.""",
    'author': 'Therp BV',
    'website': 'http://www.therp.nl',
    "category": "Tools",
    "depends": [],
    "data": ['ir_model_fields.xml'],
    'installable': True,
    'active': False,
}
