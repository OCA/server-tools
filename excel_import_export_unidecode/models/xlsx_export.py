# Copyright 2023 FactorLibre (https://factorlibre.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import unidecode

from odoo import models

from . import common as co


class XLSXExport(models.AbstractModel):
    _inherit = "xlsx.export"

    def _get_conditions_dict(self):
        res = super()._get_conditions_dict()
        res.setdefault("field_unidecode_dict", {})
        return res

    def run_field_unidecode_dict(self, field):
        return co.get_field_unidecode(field)

    def apply_extra_conditions_to_value(self, field, value, conditions_dict):
        res = super().apply_extra_conditions_to_value(field, value, conditions_dict)
        if conditions_dict["field_unidecode_dict"][field[0]] and (
            isinstance(res, bytes) or isinstance(res, str)
        ):
            if isinstance(res, bytes):
                res = res.decode("utf-8")
            res = unidecode.unidecode(res)
        return res
