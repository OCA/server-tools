# Copyright 2024 Camptocamp (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import api, models


class IrModelData(models.Model):
    _inherit = "ir.model.data"

    @api.model_create_multi
    def create(self, vals_list):
        noupdate_models = self.env["ir.model"].sudo()._get_noupdate_models()
        if noupdate_models:
            noupdate_model_names = set(noupdate_models.mapped("model"))
            for vals in vals_list:
                if vals.get("model") in noupdate_model_names:
                    vals["noupdate"] = True
        return super().create(vals_list)
