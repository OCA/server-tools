from odoo import api, models
from odoo.tools import html2plaintext


class MailTracking(models.Model):
    _inherit = "mail.tracking.value"

    @api.model
    def _create_tracking_values(
        self, initial_value, new_value, col_name, col_info, record
    ):
        try:
            return super()._create_tracking_values(
                initial_value, new_value, col_name, col_info, record
            )
        except NotImplementedError:
            if col_info["type"] == "html":
                field = self.env["ir.model.fields"]._get(record._name, col_name)
                values = {"field_id": field.id}
                values.update(
                    {
                        "old_value_char": html2plaintext(initial_value) or "",
                        "new_value_char": html2plaintext(new_value) or "",
                    }
                )
                return values
            raise
