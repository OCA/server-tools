# Copyright 2021-2024 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrRule(models.Model):
    _inherit = "ir.rule"

    auditlog_line_access_rule_id = fields.Many2one(
        "auditlog.line.access.rule",
        required=False,
        index=True,
        ondelete="cascade",
        help="Auditlog line access Rule that generated this ir.rule",
    )
