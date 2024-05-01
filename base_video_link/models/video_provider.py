# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VideoProvider(models.Model):
    _name = "video.provider"
    _description = "Video Provider"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    pattern_video_url = fields.Char(
        default="https://example.org/video/%s", required=True
    )
    pattern_thumbnail_url = fields.Char(
        default="https://example.org/thumbnail/%s", required=True
    )
