# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import html2plaintext


class MailTrackMixin(models.AbstractModel):
    _inherit = "mail.track.mixin"

    @api.ormcache("self.env.uid", "self.env.su")
    def _track_get_fields(self):
        fields_per_models = self.env["ir.model"]._get_custom_tracked_fields_per_model()
        if self._name in fields_per_models:
            return set(self.fields_get(fields_per_models[self._name]))
        return super()._track_get_fields()

    def _create_mail_tracking_values(
        self, initial_value, new_value, col_name, col_info
    ):
        try:
            return super()._create_mail_tracking_values(
                initial_value, new_value, col_name, col_info
            )
        except NotImplementedError:
            if col_info.get("type") == "html":
                field = self.env["ir.model.fields"]._get(self._name, col_name)
                old_val = html2plaintext(initial_value) or ""
                new_val = html2plaintext(new_value) or ""
                return {
                    "field_id": field.id,
                    "field_name": col_name,
                    "field_label": (
                        col_info.get("string")
                        if "string" in col_info
                        else field.field_description
                    ),
                    "field_type": col_info["type"],
                    "old_value_char": old_val,
                    "new_value_char": new_val,
                    "old_value": old_val or "None",
                    "new_value": new_val or "None",
                }
            raise
