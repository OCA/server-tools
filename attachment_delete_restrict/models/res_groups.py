# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    delete_attachment_model_ids = fields.Many2many(
        "ir.model",
        string="Attachment Deletion Models",
        help="The users of the group can delete the attachments related to "
        "the models "
        "assigned here. In general settings, 'Restrict Delete "
        "Attachment' must be set as 'custom' to activate this setting.",
    )
