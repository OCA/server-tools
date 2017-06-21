# -*- coding: utf-8 -*-
# © 2015 Endika Iglesias
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Synchronize Gravatar Image',
    'version': '10.0.2.0.0',
    'author': 'LasLabs, Endika Iglesias, Odoo Community Association (OCA), Hugo Rodrigues',
    'category': 'Tools',
    'website': 'https://odoo-community.org/',
    "license": "AGPL-3",
    "application": False,
    'installable': True,
    'data': [
        'views/res_users_view.xml',
        'data/cron.xml',
        'data/ir_parameter.xml'
    ],
}
