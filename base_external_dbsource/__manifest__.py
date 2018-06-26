# -*- coding: utf-8 -*-
# Copyright 2011 Daniel Reis, Maxime Chambreuil, Savoir-faire Linux
# Copyright 2016 LasLabs Inc.
# Copyright 2017 Henry Zhou <zhouhenry@live.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'External Database Sources',
    'version': '11.0.1.0.0',
    'category': 'Tools',
    'author': "Daniel Reis, "
              "LasLabs, "
              "Henry Zhou, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/server-tools',
    'license': 'LGPL-3',
    'images': [
        'images/screenshot01.png',
    ],
    'depends': [
        'base',
    ],
    'data': [
        'views/base_external_dbsource.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/base_external_dbsource.xml',
    ],
    'installable': True,
}
