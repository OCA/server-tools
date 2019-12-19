# Copyright 2015 Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2015 Antiun Ingeniería S.L. - Carlos Dauden
# Copyright 2015-2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

{
    'name': "Base Custom Info",
    'summary': "Add custom field in models",
    'category': 'Tools',
    'version': '12.0.1.0.1',
    'depends': [
        'base_setup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups_security.xml',
        'views/custom_info_category_view.xml',
        'views/custom_info_option_view.xml',
        'views/custom_info_template_view.xml',
        'views/custom_info_property_view.xml',
        'views/custom_info_value_view.xml',
        'views/menu.xml',
        'views/res_partner_view.xml',
        'wizard/res_config_settings_view.xml',
    ],
    'demo': [
        'demo/custom.info.category.csv',
        'demo/custom.info.template.csv',
        'demo/custom.info.property.csv',
        'demo/custom.info.option.csv',
        'demo/res_groups.xml',
        'demo/defaults.xml',
    ],
    "images": [
        "images/menu.png",
        "images/properties.png",
        "images/templates.png",
        "images/values.png",
    ],
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
}
