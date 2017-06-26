# -*- coding: utf-8 -*-
# Copyright 2015 GRAP - Sylvain LE GAL
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Authentification - Brute-force Attack',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'summary': "Tracks Authentication Attempts and Prevents Brute-force"
               " Attacks module",
    'author': "GRAP, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'web',
        ],
    'data': [
        'security/ir_model_access.yml',
        'data/ir_config_parameter.xml',
        'views/view.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
