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
    'description': """
Sparse, or serialized fields do not live as a column in the database table.
Instead, their values are stored in JSON arrays in a separate field. As a
result, these fields cannot be searched or sorted by.

If such a sparse field is created as 'manual', this module can unserialize
the field. Its field definition and values will then be migrated to a
proper database column. A real life use case where you encounter many
of such fields is the Magento-OpenERP connector.

For technical reasons, many2many and one2many fields are not supported.
""",
    'author': 'Therp BV',
    'website': 'http://www.therp.nl',
    'version': '1.0',
    "category": "Tools",
    "depends": ['base'],
    "data": ['ir_model_fields.xml'],
    'installable': True,
    'active': False,
}
