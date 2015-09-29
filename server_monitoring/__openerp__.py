# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2014 Camptocamp SA
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
    'name': 'Server Monitoring',
    'version': '8.0.1.0.0',
    'category': 'Tools',
    'depends': [],
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'data': [
        'views/menu.xml',
        'views/server_monitor_database_table_activity.xml',
        'views/server_monitor_database.xml',
        'views/server_monitor_model_row_count.xml',
        'views/server_monitor_model_table_size.xml',
        'views/server_monitor_process.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        ],
    'test': [
        'tests/test_monitor_process.yml',
        'tests/test_monitor_database.yml',
        ],
    'installable': True,
}
