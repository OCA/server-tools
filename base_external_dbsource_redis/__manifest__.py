# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'External Database Source - Redis',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'author': "LasLabs, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/server-tools',
    'license': 'LGPL-3',
    'depends': [
        'base_external_dbsource',
    ],
    'external_dependencies': [
        'python': [
            'redis',
        ],
    ],
    'demo': [
        'demo/base_external_dbsource.xml',
    ],
    'installable': True,
}
