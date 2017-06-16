# -*- coding: utf-8 -*-
# Copyright 2015 Antiun Ingeniería S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Manage model export profiles",
    'category': 'Personalization',
    'version': '10.0.1.0.0',
    'depends': [
        'web',
    ],
    'data': [
        'views/assets.xml',
        'views/ir_exports.xml',
        'views/ir_model.xml',
        'views/ir_model_access.xml',
        'views/res_groups.xml',
    ],
    'qweb': [
        "static/src/xml/base.xml",
    ],
    'author': 'Antiun Ingeniería S.L., '
              'Tecnativa, '
              'LasLabs, '
              'Ursa Information Systems, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.tecnativa.com',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}
