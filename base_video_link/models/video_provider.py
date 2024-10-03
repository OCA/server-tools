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
        default="https://example.org/video/{record.identifier}",
        required=True,
        help="Pattern to generate the video's URL. "
        "`record` variable represents the video record.",
    )
    pattern_thumbnail_url = fields.Char(
        default="https://example.org/thumbnail/{record.identifier}",
        required=True,
        help="Pattern to generate the video's thumb URL. "
        "`record` variable represents the video record.",
    )
