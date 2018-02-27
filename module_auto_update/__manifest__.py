# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Module Auto Update',
    'summary': 'Automatically update Odoo modules',
    'version': '11.0.1.0.0',
    'category': 'Extra Tools',
    'website': 'https://odoo-community.org/',
    'author': 'LasLabs, '
              'Juan José Scarafía, '
              'Tecnativa, '
              'ACSONE SA/NV, '
              'Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'depends': [
        'base',
    ],
    'data': [
        'data/cron_data_deprecated.xml',
    ],
}
