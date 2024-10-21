# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class XLSXTemplate(models.Model):
    _inherit = "xlsx.template"

    available_on_mail = fields.Boolean()
    mail_template_ids = fields.One2many(
        "mail.template", "export_template_id", string="Mail Template"
    )
