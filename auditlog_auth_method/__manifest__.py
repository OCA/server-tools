# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Audit Log Authentication Method",
    "summary": "Record and filter audit logs by the authentication method used",
    "version": "17.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["GuillemCForgeFlow"],
    "license": "AGPL-3",
    "depends": ["auditlog"],
    "data": [
        "security/ir.model.access.csv",
        "data/auditlog_auth_method_data.xml",
        "views/auditlog_rule_views.xml",
        "views/auditlog_log_views.xml",
        "views/auditlog_http_request_views.xml",
        "views/auditlog_auth_method_views.xml",
    ],
    "post_load": "post_load_hook",
}
