# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia - Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

{
    'name': u'Multi localization',
    'version': '10.0.1.0.0',
    'author': u'Ari Caldeira',
    'maintainer': u'Taŭga Tecnologia',
    'category': u'Base',
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
    ]
}
