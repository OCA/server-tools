# -*- coding: utf-8 -*-
# © 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Base merge',
    'version': '10.0.0.0.0',
    'author': 'Therp BV, Odoo Community Association (OCA), Odoo SA',
    'category': 'Server Tools',
    'summary': """This module enables merging
    of duplicate records for a model""",
    'website': 'http://www.therp.nl',
    'license': 'AGPL-3',
    'depends': ['base'],
    'data': [
        'views/base_merge_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
