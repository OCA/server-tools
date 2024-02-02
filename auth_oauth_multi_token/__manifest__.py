# -*- coding: utf-8 -*-
# Copyright 2016 Florent de Labarre
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'OAuth Multi Token',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Florent de Labarre, '
              'Camptocamp, '
              'Odoo Community Association (OCA)',
    'summary': """Allow multiple connection with the same OAuth account""",
    'category': 'Tool',
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/auth_oauth_multi_token',
    'depends': ['auth_oauth'],
    'data': [
        'views/res_users.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
