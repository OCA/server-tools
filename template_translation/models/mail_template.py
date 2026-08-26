# Copyright 2024 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class MailTemplate(models.Model):
    """Add mail template to mail.mail."""

    _inherit = "mail.template"

    def generate_email(self, *args, **kwargs):
        """Store id of this template with mail to be created."""
        result = super().generate_email(*args, **kwargs)
        result["mail_template_id"] = self.id  # Super checks self.ensure_one()
        return result
