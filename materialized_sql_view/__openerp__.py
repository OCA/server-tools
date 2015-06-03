# =============================================================================
#                                                                             =
#    materialized_sql_view module for OpenERP,                                =
#    Copyright (C) 2013 Anybox (<http://http://anybox.fr>)                    =
#                         Pierre Verkest <pverkest@anybox.fr>                 =
#                                                                             =
#    This file is a part of materialized_sql_view                             =
#                                                                             =
#    materialized_sql_view is free software: you can redistribute it and/or   =
#    modify it under the terms of the GNU Affero General Public License v3 or =
#    later as published by the Free Software Foundation, either version 3 of  =
#    the License, or (at your option) any later version.                      =
#                                                                             =
#    materialized_sql_view is distributed in the hope that it will be useful, =
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           =
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            =
#    GNU Affero General Public License v3 or later for more details.          =
#                                                                             =
#    You should have received a copy of the GNU Affero General Public License =
#    v3 or later along with this program.                                     =
#    If not, see <http://www.gnu.org/licenses/>.                              =
#                                                                             =
# =============================================================================
{
    'name': 'Materialized Sql View',
    'version': '0.1',
    'category': 'Tools',
    'author': 'Pierre Verkest,Odoo Community Association (OCA)',
    'maintainer': 'Odoo Community Association (OCA)',
    'depends': [
        'base',
        'web',
    ],
    'demo_xml': [
    ],
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'views/materialized_sql_view.xml',
        'menus/menus.xml',
    ],
    'js': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
