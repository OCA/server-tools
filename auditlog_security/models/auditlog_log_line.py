# Copyright 2022 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, models, fields


class AuditlogLogLine(models.Model):
    _inherit = 'auditlog.log.line'
    _order = "create_date desc"

    user_id = fields.Many2one(
        'res.users',
        compute="compute_user_id",
        store=True,
        index=True,
        string="User",
    )
    method = fields.Char("Method", compute='compute_method', store=True, index=True)
    model_id = fields.Many2one(
        "ir.model", 
        compute='compute_model_id', 
        store=True, 
        index=True)
    res_id = fields.Integer(
        compute='compute_res_id', 
        store=True, 
        index=True)

    @api.depends('log_id.method')
    def compute_method(self):
        for this in self:
            this.method=this.log_id.method

    @api.depends('log_id.user_id')
    def compute_user_id(self):
        for this in self:
            this.user_id=this.log_id.user_id

    @api.depends('log_id.model_id')
    def compute_model_id(self):
        for this in self:
            this.model_id=this.log_id.model_id
    
    @api.depends('log_id.res_id')
    def compute_res_id(self):
        for this in self:
            this.res_id=this.log_id.res_id
