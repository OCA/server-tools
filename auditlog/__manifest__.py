# © 2015 ABF OSIELL <https://osiell.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': "Audit Log",
    'version': "11.0.1.0.0",
    'author': "ABF OSIELL,Odoo Community Association (OCA)",
    'license': "AGPL-3",
    'website': "https://www.osiell.com",
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
}
