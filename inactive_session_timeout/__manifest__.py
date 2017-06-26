# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE - Cédric Pigeon
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Inactive Sessions Timeout",
    'version': '10.0.1.0.0',
    'author': "ACSONE SA/NV, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'https://www.tecnativa.com',
    'category': 'Tools',
    'summary': 'This module disable all inactive sessions since a given delay',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'data/ir_config_parameter_data.xml'
    ],
    'installable': True,
}
