# -*- coding: utf-8 -*-
# Author: Alexandre Fayolle
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Server Monitoring',
    'version': '8.0.1.0.0',
    'category': 'Tools',
    'depends': ['web', 'base_setup'],
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'data': [
        'views/menu.xml',
        'views/server_monitor_database_table_activity.xml',
        'views/server_monitor_database.xml',
        'views/server_monitor_model_row_count.xml',
        'views/server_monitor_model_table_size.xml',
        'views/server_monitor_process.xml',
        'views/res_config.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        ],
    'test': [
        'tests/test_monitor_process.yml',
        'tests/test_monitor_database.yml',
        ],
    'installable': True,
}
