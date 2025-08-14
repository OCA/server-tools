# Copyright 2025 glueckkanja AG (<https://www.glueckkanja.com>) - Christopher Rogos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    tracking_domain = fields.Char(
        help="Add a domain filter to only track changes when"
        " certain condition apply on the parent record."
    )

    def write(self, vals):
        if "tracking_domain" in vals:
            self.env.registry.clear_cache()
            self.check_access("write")
            custom_tracking_domain = vals.pop("tracking_domain")
            self._write({"tracking_domain": custom_tracking_domain})
            self.invalidate_model(fnames=["tracking_domain"])
        return super().write(vals)
