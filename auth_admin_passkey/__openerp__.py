# -*- coding: utf-8 -*-
# © 2016 GRAP
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# -*- encoding: utf-8 -*-

{
    'name': 'Authentification - Admin Passkey',
    'version': '9.0.1.0.0',
    'category': 'base',
    'author': "GRAP,Odoo Community Association (OCA)",
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'mail',
        ],
    'data': [
        'data/ir_config_parameter.xml',
        'view/res_config_view.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
