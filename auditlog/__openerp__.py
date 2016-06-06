# -*- coding: utf-8 -*-
# © 2015 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Audit Log",
    'version': "9.0.1.0.0",
    'author': "ABF OSIELL,Odoo Community Association (OCA)",
    'license': "AGPL-3",
    'website': "http://www.osiell.com",
    'category': "Tools",
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/auditlog_view.xml',
        'views/http_session_view.xml',
        'views/http_request_view.xml',
    ],
    'application': True,
    'installable': True,
    'pre_init_hook': 'pre_init_hook',
}
