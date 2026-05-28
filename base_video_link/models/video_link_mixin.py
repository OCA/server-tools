# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VideoLinkMixin(models.AbstractModel):
    _name = "video.link.mixin"
    _description = "Video Link Mixin"

    video_ids = fields.Many2many(comodel_name="video.video", string="Video")
