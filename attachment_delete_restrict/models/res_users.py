# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    delete_attachment_model_ids = fields.Many2many(
        "ir.model",
        relation="delete_attachment_user_rel",
        string="Attachment Deletion Models",
        help="The user can delete the attachments related to the models "
        "assigned here. Restrict Attachment Deletion must be"
        "'Custom' or 'Owner + Custom' for the model to be selected here.",
    )
