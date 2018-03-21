# Copyright (C) 2018-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Synchronize Gravatar Image',
    'version': '11.0.0.0.0',
    'author': 'LasLabs, Endika Iglesias, ACSONE SA/NV, '
              'Odoo Community Association (OCA)',
    'category': 'Tools',
    'website': 'https://odoo-community.org/',
    "license": "AGPL-3",
    "application": True,
    'installable': True,
    'data': [
        'data/ir_config_parameter.xml',
        'views/res_users_view.xml',
    ],
}
