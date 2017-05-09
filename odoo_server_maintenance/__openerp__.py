# -*- coding: utf-8 -*-

{
    'name': 'Server Lock for Maintenance Mode',
    'version': '8.0.1.0.0',
    'author': 'Ecosoft,Odoo Community Association (OCA)',
    'category': 'Hidden',
    'description': """
This module will lock server for maintenance mode by \n
1. Set users in group manage maintenance mode. \n
2. Select change maintenance mode under more button in users menu
   which user is in group manage maintenance mode will not select
   maintenance mode and if user not in group manage maintenance mode will
   can not manage maintenance mode. \n
3. User is in maintenance mode can not login and show message
   'This user is in maintenance mode'. \n
If user is not maintenance mode user will normal login.
    """,
    'website': 'http://ecosoft.co.th',
    'depends': [
        'web',
    ],
    'data': [
        'wizards/change_maintenance_mode_view.xml',
        'views/res_users_view.xml',
        'security/odoo_server_maintenance_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartinden't:tabstop=4:softtabstop=4:shiftwidth=4:
