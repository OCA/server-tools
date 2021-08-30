# Copyright 2021 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    restrict_update = fields.Boolean(
        "Update Restrict Model",
        help="When selected, the model is restricted to read-only unless the "
        "user has the special permission.",
    )
    restrict_update_method = fields.Selection(
        selection=[
            ("model", "Model Restriction"),
            ("user", "User Restriction"),
        ],
        compute="_compute_restrict_update_method",
    )

    def _compute_restrict_update_method(self):
        Config = self.env["res.config.settings"]
        for rec in self:
            rec.restrict_update_method = Config.get_values().get(
                "restrict_update_method"
            )
