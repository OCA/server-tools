# Copyright 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResRequestLink(models.Model):
    _inherit = "res.request.link"

    ext_attachment_sync = fields.Boolean(
        string="External Attachment Sync",
        default=True,
        index=True,
        help="Sync Attachments of this model to External Storage")
