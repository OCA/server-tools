# Copyright 2026 Syed Sameed Zafar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "phone.autoformat.mixin"]

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([self._autoformat_vals(dict(v)) for v in vals_list])

    def write(self, vals):
        return super().write(self._autoformat_vals(dict(vals)))
