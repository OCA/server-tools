# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
# Copyright 2016 Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

{
    'name': 'Multi localization',
    'version': '10.0.1.0.0',
    'author': u'Ari Caldeira, Odoo Community Association (OCA)',
    'maintainer': u'Taŭga Tecnologia',
    'license': 'AGPL-3',
    'category': 'Base',
    'depends': [
        'base',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'data': [
        'views/ir_localization_view.xml',
        'views/ir_ui_view_view.xml',
        'views/res_users_view.xml',
        'views/res_company_view.xml',
        'security/ir.model.access.csv',
    ]
}
