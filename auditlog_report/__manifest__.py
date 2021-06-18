# Copyright 2021 Ecosoft Co., Ltd. <http://ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Audit Log Report",
    "version": "14.0.1.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": ["auditlog"],
    "data": [
        "security/ir.model.access.csv",
        "report/auditlog_report.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": True,
}
