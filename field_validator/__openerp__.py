# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "Fields Validator",
    'version': '0.1',
    'category': 'Tools',
    'summary': "",
    'description': """
This module allows to set a regular expresion as field validator.
When the regular expresion is set, write and create operations on the involved
field are blocked, if the regular expression is not satisfied.
See demo and test data for an example with partner email.
""",
    'author': 'Agile Business Group',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": ['base'],
    "data": [
        'ir_model_view.xml',
        'security/ir.model.access.csv',
        ],
    "demo": [
        'ir_model_demo.xml',
        ],
    'test': [
        'test/validator.yml',
    ],
    "active": False,
    "installable": True
}
