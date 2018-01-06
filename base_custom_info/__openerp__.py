# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Base Custom Info",
    'summary': "Add custom field in models",
    'category': 'Customize',
    'version': '8.0.1.0.0',
    'depends': [
        'base',
    ],
    'data': [
        'views/custom_info_template_view.xml',
        'views/custom_info_template_line_view.xml',
        'views/custom_info_value_view.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],
    'author': 'Antiun Ingeniería S.L., '
              'Incaser Informatica S.L., ',
    'website': 'http://www.antiun.com',
    'license': 'AGPL-3',
    'installable': True,
}
