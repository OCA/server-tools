# -*- coding: utf-8 -*-

{
    'name': 'User Maintenance Mode',
    'version': '8.0.1.0.0',
    'author': 'Tharathip C.,Ecosoft,Odoo Community Association (OCA)',
    'category': 'Hidden',
    'description': """
    """,
    'website': 'http://ecosoft.co.th',
    'depends': [
        'web',
    ],
    'data': [
        'security/user_maintenance_mode_security.xml',
        'views/res_users_view.xml',
        'wizards/change_maintenance_mode_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
