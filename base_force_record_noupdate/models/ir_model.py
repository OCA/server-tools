# Copyright 2024 Camptocamp (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import api, fields, models
from odoo.tools import ormcache


class IrModel(models.Model):
    _inherit = "ir.model"

    force_noupdate = fields.Boolean("Force No-Update")

    @api.model_create_multi
    def create(self, vals_list):
        mods = super().create(vals_list)
        self.env.registry.clear_cache()
        self._propagate_noupdate_to_model_data()
        return mods

    def write(self, vals):
        res = super().write(vals)
        if "force_noupdate" in vals:
            self.env.registry.clear_cache()
            self._propagate_noupdate_to_model_data()
        return res

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_cache()
        return res

    def _get_noupdate_models(self):
        return self.browse(self._get_noupdate_model_ids())

    @ormcache()
    def _get_noupdate_model_ids(self):
        return self.search([("force_noupdate", "=", True)]).ids

    @api.model
    def _propagate_noupdate_to_model_data(self):
        noupdate = self._get_noupdate_models().mapped("model")
        imd = self.env["ir.model.data"].sudo()
        model_data = imd.search([("model", "in", noupdate), ("noupdate", "=", False)])
        if model_data:
            model_data.write({"noupdate": True})

    def toggle_force_noupdate(self):
        true_to_false = self.filtered("force_noupdate")
        if true_to_false:
            true_to_false.write({"force_noupdate": False})
        false_to_true = self - true_to_false
        if false_to_true:
            false_to_true.write({"force_noupdate": True})
