# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    'name': 'Security Profiler',
    'version': '11.0.1.0.0',
    'summary': 'Logs the security workflow of an user',
    'author': 'Eficent,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_profiler_views.xml',
        'reports/report_template.xml',
        'reports/report_user_role_group.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
