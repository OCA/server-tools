# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VideoVideo(models.Model):
    _name = "video.video"
    _description = "Video"
    _order = "sequence, name"

    sequence = fields.Integer()
    name = fields.Char(required=True)
    provider_id = fields.Many2one("video.provider", "Provider", required=True)
    identifier = fields.Char(required=True)
    url = fields.Char(compute="_compute_url")
    thumbnail_url = fields.Char(compute="_compute_url")

    @api.depends("identifier", "provider_id")
    def _compute_url(self):
        for record in self:
            record.url = ""
            record.thumbnail_url = ""
            provider = record.provider_id
            if provider.pattern_video_url:
                record.url = provider.pattern_video_url.format(record=record)
            if provider.pattern_thumbnail_url:
                record.thumbnail_url = provider.pattern_thumbnail_url.format(
                    record=record
                )
