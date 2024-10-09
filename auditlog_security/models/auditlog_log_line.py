# Copyright 2022-2024 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AuditlogLogLine(models.Model):
    _inherit = "auditlog.log.line"
    _order = "create_date desc"

    user_id = fields.Many2one(
        "res.users",
        compute="_compute_user_id",
        store=True,
        index=True,
        string="User",
    )
    method = fields.Char(compute="_compute_method", store=True, index=True)
    model_id = fields.Many2one(
        "ir.model", compute="_compute_model_id", store=True, index=True
    )
    res_id = fields.Integer(compute="_compute_res_id", store=True, index=True)

    @api.depends("log_id.method")
    def _compute_method(self):
        for this in self:
            this.method = this.log_id.method

    @api.depends("log_id.user_id")
    def _compute_user_id(self):
        for this in self:
            this.user_id = this.log_id.user_id

    @api.depends("log_id.model_id")
    def _compute_model_id(self):
        for this in self:
            this.model_id = this.log_id.model_id

    @api.depends("log_id.res_id")
    def _compute_res_id(self):
        for this in self:
            this.res_id = this.log_id.res_id
