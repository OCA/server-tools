# Copyright 2021 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    unrestrict_model_update = fields.Boolean(
        string="Grant Update Permit",
        help="Set to true and the user can update restricted model.",
    )
    restrict_model_update = fields.Boolean(
        string="Restrict Update Permit",
        compute="_compute_restrict_model_update",
        inverse="_inverse_restrict_model_update",
        help="Set to true and user are restricted from model update.",
    )
    restrict_update_method = fields.Selection(
        selection=[
            ("model", "Model Restriction"),
            ("user", "User Restriction"),
        ],
        compute="_compute_restrict_update_method",
    )

    @api.depends("unrestrict_model_update")
    def _compute_restrict_model_update(self):
        for rec in self:
            rec.restrict_model_update = not rec.unrestrict_model_update

    def _inverse_restrict_model_update(self):
        for rec in self:
            rec.unrestrict_model_update = not rec.restrict_model_update

    def _compute_restrict_update_method(self):
        Config = self.env["res.config.settings"]
        for rec in self:
            rec.restrict_update_method = Config.get_values().get(
                "restrict_update_method"
            )

    def toggle_unrestrict_model_update(self):
        for record in self:
            record.unrestrict_model_update = not record.unrestrict_model_update
