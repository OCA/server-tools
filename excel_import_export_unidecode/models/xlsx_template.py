# Copyright 2023 FactorLibre (https://factorlibre.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


from odoo import api, fields, models

from . import common as co


class XLSXTemplate(models.Model):
    _inherit = "xlsx.template"

    def _compose_field_name(self, line):
        res = super()._compose_field_name(line)
        if line.is_unidecode:
            res += "@?unidecode?"
        return res


class XLSXTemplateExport(models.Model):
    _inherit = "xlsx.template.export"

    is_unidecode = fields.Boolean(string="Unidecode", default=False)

    @api.model
    def _extract_field_name(self, vals):
        res = super()._extract_field_name(vals)
        if self._context.get("compute_from_input") and res.get("field_name"):
            field_name, func_unidecode = co.get_field_unidecode(res.get("field_name"))
            res.update(
                {
                    "field_name": field_name,
                    "is_unidecode": func_unidecode,
                }
            )

        return res
