# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class Translation(models.Model):
    _inherit = "ir.translation"

    @api.model
    def _upsert_translations(self, vals_list):
        if self.env.context.get("skip_translation_copy"):
            to_skip = []
            for model_name, model in self.env.items():
                field_names = model._get_field_names_to_skip_in_copy()
                if field_names:
                    to_skip.extend([f"{model_name},{f}" for f in field_names])
            vals_list = [v for v in vals_list if v.get("name") not in to_skip]
        return super()._upsert_translations(vals_list)
