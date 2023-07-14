# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    field_label = fields.Char(string="Translated Field", compute="_compute_field_label")

    value = fields.Text(string="Translated Value")

    @api.depends("name")
    def _compute_field_label(self):
        for it in self:
            field_label = it.name
            if it.name and "," in it.name and it.name.count(",") == 1:
                model_name, field_name = it.name.split(",")
                model = self.env.get(model_name)
                if model is not None and field_name in model._fields:
                    field_label = model._fields[field_name].string
            it.field_label = field_label
