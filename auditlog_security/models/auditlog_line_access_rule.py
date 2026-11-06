# Copyright 2021-2024 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AuditlogLineAccessRule(models.Model):
    _name = "auditlog.line.access.rule"
    _description = "Auditlog Line Access Rule"

    name = fields.Char()

    field_ids = fields.Many2many("ir.model.fields")
    group_ids = fields.Many2many(
        "res.groups",
        help="""Groups that will be allowed to see the logged fields, if left empty
                default will be all users with a login""",
    )
    model_id = fields.Many2one(
        "ir.model", related="auditlog_rule_id.model_id", readonly=True
    )
    auditlog_rule_id = fields.Many2one(
        "auditlog.rule", "auditlog_access_rule_ids", readonly=True, ondelete="cascade"
    )
    state = fields.Selection(related="auditlog_rule_id.state", readonly=True)
