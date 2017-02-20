# -*- coding: utf-8 -*-
# © 2014-2017 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Database cleanup',
    'version': '8.0.0.3.0',
    'author': "Therp BV,Odoo Community Association (OCA)",
    'depends': ['base'],
    'license': 'AGPL-3',
    'category': 'Tools',
    'data': [
        'views/purge_wizard.xml',
        'views/purge_menus.xml',
        'views/purge_modules.xml',
        'views/purge_models.xml',
        'views/purge_columns.xml',
        'views/purge_tables.xml',
        'views/purge_data.xml',
        'views/create_indexes.xml',
        'views/purge_properties.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
