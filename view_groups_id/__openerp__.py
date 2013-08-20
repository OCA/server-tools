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
    'name': 'group_ids for ir.ui.view',
    'version': '1.0',
    'description': """This addon is a backport of OpenERP 7.0's groups_id for
    views.
    
    The greatness lies in the fact that with that, you can have specific
    inherited views for specific groups, so you can radically change a view
    for some groups without having to redefine any of the window actions
    involved.

    Using it for 6.1 modules instead of fields_view_get hacks and the like
    also lowers the effort it takes to port the module in question to 7.0
    """,
    'author': ['Therp BV', 'OpenERP SA'],
    'website': 'http://www.therp.nl',
    "category": "Dependency",
    "depends": [
        'base',
        ],
    'css': [
        ],
    'data': [
        'view/ir_ui_view.xml',
        ],
    'js': [
        ],
    'installable': True,
    'active': False,
    'certificate': '',
}
