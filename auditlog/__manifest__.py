# Copyright 2015 ABF OSIELL <https://osiell.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Audit Log",
    "version": "19.0.1.0.1",
    "author": "ABF OSIELL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": ["base"],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/menu.xml",
        "views/auditlog_http_request_views.xml",
        "views/auditlog_http_session_views.xml",
        "views/auditlog_log_line_views.xml",
        "views/auditlog_log_views.xml",
        "views/auditlog_rule_views.xml",
    ],
    "application": True,
    "installable": True,
}
