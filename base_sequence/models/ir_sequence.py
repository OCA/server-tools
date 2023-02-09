# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class IrSequence(models.Model):
    """
    This sub-class is to refactor the ir.sequence by changing the inextensible
    inner function `_interpolation_dict()` to a normal private class function.
    """

    _inherit = "ir.sequence"

    preview = fields.Char(compute="_compute_preview")

    @api.depends(
        "prefix",
        "suffix",
        "padding",
        "use_date_range",
        "number_next_actual",
        "implementation",
    )
    def _compute_preview(self):
        if self.use_date_range:
            self.date_range_ids._compute_preview()
            self.preview = None
        else:
            self.preview = self.get_next_char(self.number_next_actual)

    def _interpolation_dict(self, date=None, date_range=None):
        """
        This private method enables other module to add more legends.
        """
        now = range_date = effective_date = datetime.now(
            pytz.timezone(self._context.get("tz") or "UTC")
        )
        if date or self._context.get("ir_sequence_date"):
            effective_date = fields.Datetime.from_string(
                date or self._context.get("ir_sequence_date")
            )
        if date_range or self._context.get("ir_sequence_date_range"):
            range_date = fields.Datetime.from_string(
                date_range or self._context.get("ir_sequence_date_range")
            )

        sequences = {
            "year": "%Y",
            "month": "%m",
            "day": "%d",
            "y": "%y",
            "doy": "%j",
            "woy": "%W",
            "weekday": "%w",
            "h24": "%H",
            "h12": "%I",
            "min": "%M",
            "sec": "%S",
        }

        res = {}
        range_end_date = fields.Datetime.from_string(
            self._context.get("ir_sequence_date_range_end")
        )
        xx = effective_date.strftime("%Y-%m-%d")
        datetime.strptime(xx, "%Y-%m-%d")
        for key, fmt in sequences.items():
            res[key] = effective_date.strftime(fmt)
            res["range_" + key] = range_date.strftime(fmt)
            res["current_" + key] = now.strftime(fmt)
            res["range_end_" + key] = (
                range_end_date.strftime(fmt) if range_end_date else None
            )
        # Quarter
        res["qoy"] = str((int(res["month"]) - 1) // 3 + 1)
        res["range_qoy"] = str((int(res["range_month"]) - 1) // 3 + 1)
        res["current_qoy"] = str((int(res["current_month"]) - 1) // 3 + 1)
        res["range_end_qoy"] = (
            str((int(res["range_end_month"]) - 1) // 3 + 1) if range_end_date else None
        )
        # Period month
        diff_period_month = (
            (effective_date.year - range_date.year) * 12
            + effective_date.month
            - range_date.month
            + 1
        )
        res["range_period_month"] = str(diff_period_month).zfill(2)
        return res

    def _get_prefix_suffix(self, date=None, date_range=None):
        """
        Override the `_get_prefix_suffix()`. This utilizes the private
        `_interpolation_dict()` instead of an inner function.
        """
        self.ensure_one()
        d = self._interpolation_dict(date=date, date_range=date_range)

        try:
            interpolated_prefix = (self.prefix % d) if self.prefix else ""
            interpolated_suffix = (self.suffix % d) if self.suffix else ""
        except KeyError as e:
            raise UserError(
                _("Invalid prefix or suffix for sequence '%s'") % (self.name)
            ) from e
        return interpolated_prefix, interpolated_suffix
