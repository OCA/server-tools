# Copyright 2024 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MailMail(models.Model):
    """Add mail template to mail.mail."""

    _inherit = "mail.mail"

    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        readonly=True,
    )
