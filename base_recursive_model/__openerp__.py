# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Buron. Copyright Yannick Buron
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Base recursive model',
    'version': '1.0',
    'category': 'base',
    'author': 'Yannick Buron',
    'license': 'AGPL-3',
    'description': """
Base recursive model
====================

Create two abstract model which can be used to manage recursive relations
-------------------------------------------------------------------------
    * Easily create recursive model (instead of having to create parent_id
        each time, you now just have to inherit the abstract model
    * Define configuration fields which can then be inherited and overridden
        by children and children models
""",
    'website': 'https://github.com/YannickB/community-management',
    'depends': ['base'],
    'data': ['security/ir.model.access.csv'],
    'installable': True,
}
