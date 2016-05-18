# -*- coding: utf-8 -*-
# © 2012-2013 Akretion Sébastien BEAU,David Beal,Alexis de Lattre
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Scheduler Error Mailer',
    'version': '9.0.1.0.0',
    'category': 'Extra Tools',
    'license': 'AGPL-3',
    'author': "Akretion,Sodexis,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['mail'],
    'data': [
        'data/ir_cron_email_tpl.xml',
        'views/ir_cron.xml',
    ],
    'demo': ['demo/ir_cron_demo.xml'],
    'images': ['images/scheduler_error_mailer.jpg'],
    'installable': True,
}
