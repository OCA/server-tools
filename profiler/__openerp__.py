#==============================================================================
#                                                                             =
#    profiler module for OpenERP, cProfile integration for Odoo/OpenERP
#    Copyright (C) 2014 Anybox <http://anybox.fr>
#                                                                             =
#    This file is a part of profiler
#                                                                             =
#    profiler is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License v3 or later
#    as published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#                                                                             =
#    profiler is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License v3 or later for more details.
#                                                                             =
#    You should have received a copy of the GNU Affero General Public License
#    v3 or later along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#                                                                             =
#==============================================================================
{
    'name': 'profiler',
    'version': '0.1',
    'category': 'devtools',
    'description': """
    cprofile integration for Odoo/OpenERP. Check the Profiler menu in admin menu
    """,
    'author': 'Georges Racinet',
    'website': 'http://anybox.fr',
    'depends': ['base', 'web'],
    'data': [
        'security/group.xml',
    ],
    'js': [
        'static/src/js/player.js',
    ],
    'qweb': [
        'static/src/xml/player.xml',
    ],
    'css': [
        'static/src/css/player.css',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
    'post_load': 'post_load',
}
