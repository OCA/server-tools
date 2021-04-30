# Copyright 2021 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    unrestrict_model_update = fields.Boolean(
        "Unrestrict Model Update",
        help="Set to true and the user can update restricted model.",
    )

    @api.multi
    def toggle_unrestrict_model_update(self):
        for record in self:
            record.unrestrict_model_update = not record.unrestrict_model_update
