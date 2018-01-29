# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Sergio Teruel
# © 2015 Antiun Ingeniería S.L. - Carlos Dauden
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Base Custom Info",
    'summary': "Add custom field in models",
    'category': 'Tools',
    'version': '8.0.1.0.0',
    'depends': [
        'base',
    ],
    'data': [
        'views/custom_info_template_view.xml',
        'views/custom_info_property_view.xml',
        'views/custom_info_value_view.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],
    "images": [
        "images/menu.png",
        "images/properties.png",
        "images/templates.png",
        "images/values.png",
    ],
    'author': 'Antiun Ingeniería S.L., '
              'Incaser Informatica S.L., '
              'Odoo Community Association (OCA)',
    'website': 'http://www.antiun.com',
    'license': 'AGPL-3',
    'installable': False,
}
