# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class XLSXTemplateImport(models.Model):
    _inherit = "xlsx.template.import"

    required = fields.Boolean(
        default=False,
        help="If enabled, this field must be filled in the Excel file during import.",
    )

    @api.model
    def _extract_field_name(self, vals):
        vals = super()._extract_field_name(vals)
        if not (self._context.get("compute_from_input") and vals.get("field_name")):
            return vals
        field_name = vals["field_name"]
        if "@{required}" in field_name:
            vals["field_name"] = field_name.replace("@{required}", "")
            vals["required"] = True
        return vals
