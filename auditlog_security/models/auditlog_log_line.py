# Copyright 2022-2024 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools
from odoo.osv.expression import OR


class AuditlogLogLine(models.Model):
    _inherit = "auditlog.log.line"
    _order = "create_date desc"

    log_id = fields.Many2one(auto_join=True)
    user_id = fields.Many2one(related="log_id.user_id")
    method = fields.Char(related="log_id.method")
    model_id = fields.Many2one(related="log_id.model_id", store=True)
    res_id = fields.Integer(related="log_id.res_id", store=True)

    allowed_group_ids = fields.Many2many(
        "res.groups",
        compute=lambda self: self.update({"allowed_group_ids": False}),
        search="_search_allowed_group_ids",
    )

    def _auto_init(self):
        res = super()._auto_init()
        tools.create_index(
            self._cr,
            "auditlog_log__line_model_res_idx",
            self._table,
            [
                "model_id",
                "res_id",
            ],
        )
        return res

    def _search_allowed_group_ids(self, operator, value):
        access_rules = self.env["auditlog.line.access.rule"].search(
            ["|", ("group_ids", operator, value), ("group_ids", "=", False)]
        )
        domains = []
        for access_rule in access_rules:
            domain = [
                ("log_id.model_id", "=", access_rule.auditlog_rule_id.model_id.id)
            ]
            if access_rule.field_ids:
                domain.append(("field_id", "in", access_rule.field_ids.ids))
            domains.append(domain)
        return OR(domains)
