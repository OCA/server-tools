# -*- coding: utf-8 -*-

{
    'name': 'Odoo Server Lock for Maintenance',
    'version': '8.0.1.0.0',
    'author': 'Ecosoft,Odoo Community Association (OCA)',
    'category': 'Hidden',
    'description': """
This module will lock user for maintenance by selecting maintenance mode
in users menu cause that user can not login and show message
'This user is in maintenance mode' but if unselect maintenance mode that user
will normal login
    """,
    'website': 'http://ecosoft.co.th',
    'depends': [
        'web',
    ],
    'data': [
        'wizards/change_maintenance_mode_view.xml',
        'views/res_users_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartinden't:tabstop=4:softtabstop=4:shiftwidth=4:
