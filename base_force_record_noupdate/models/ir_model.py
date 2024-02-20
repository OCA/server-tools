# Copyright 2024 Camptocamp SA
# @author Italo LOPES <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class IrModelData(models.Model):

    _inherit = "ir.model.data"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        # check models that we need to protect from update
        noupdate_models = (
            self.env["ir.config_parameter"].sudo().get_param("models_force_noupdate")
        )
        if noupdate_models:
            models_force_noupdate = list(map(int, noupdate_models.split(",")))
            if models_force_noupdate:
                for vals in vals_list:
                    if (
                        vals.get("model", False)
                        and vals.get("model", False) in models_force_noupdate
                    ):
                        vals["noupdate"] = True
        return res
