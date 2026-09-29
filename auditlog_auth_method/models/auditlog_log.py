# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

MFA_METHODS = [
    ("none", "None"),
    ("totp", "Authenticator app"),
    ("totp_mail", "Email code"),
    ("other", "Other"),
]


class AuditlogLog(models.Model):
    _inherit = "auditlog.log"

    auth_method_id = fields.Many2one(
        "auditlog.auth.method",
        string="Authentication Method",
        readonly=True,
        index=True,
        ondelete="restrict",
    )
    auth_mfa_method = fields.Selection(
        MFA_METHODS,
        string="Second Factor",
        readonly=True,
    )
    auth_api_key_name = fields.Char(string="API Key", readonly=True)
    http_request_remote_addr = fields.Char(
        related="http_request_id.remote_addr",
        string="Client IP",
    )
    http_request_user_agent = fields.Char(
        related="http_request_id.user_agent",
        string="User Agent",
    )
