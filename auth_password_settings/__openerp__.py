# -*- coding: utf-8 -*-
# © Denero Team. (<http://www.deneroteam.com>)
# © 2016 Hans Henrik Gabelgaard www.steingabelgaard.dk
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'User Password Settings',
    'version': '8.0.1.0.0',
    'category': 'tools',
    'sequence': 3,
    'summary': 'User Password Settings',
    'author': 'Denero Team, '
              'Hans Henrik Gabelgaard, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.deneroteam.com',
    'license': 'AGPL-3',
    'depends': [
        'base', 'base_setup', 'auth_signup',
    ],
    'images': [
        'static/description/auth_password_settings_config.png'
        ],
    'data': [
        "data/auth_password_settings_data.xml",
        "views/res_config_view.xml",
        ],
    'installable': True,
    'auto_install': False,
}
