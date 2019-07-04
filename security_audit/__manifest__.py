# -*- coding: utf-8 -*-

{
    'name': 'Security Audit',
    'version': '1.0',
    'license': 'AGPL-3',
    'depends': ['base', 'mail'],
    'author': 'Florent de Labarre',
    'website': 'https://github.com/fmdl',
    'category': 'Tools',
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/mail_activity_data.xml',
        'views/security_audit.xml',
    ],
    'installable': True,
}
