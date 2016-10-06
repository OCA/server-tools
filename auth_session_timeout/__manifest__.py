# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Inactive Sessions Timeout",

    'summary': """
        This module disable all inactive sessions since a given delay""",

    'author': "ACSONE SA/NV, Dhinesh D, Odoo Community Association (OCA)",
    'maintainer': 'Odoo Community Association (OCA)',
    'website': "http://acsone.eu",

    'category': 'Tools',
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',

    'depends': [
        'base',
    ],

    'data': [
        'data/ir_config_parameter_data.xml'
    ],
    'installable': False,
}
