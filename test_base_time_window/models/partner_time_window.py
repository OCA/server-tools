# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import math

from odoo import _, api, fields, models


class TestPartnerTimeWindow(models.Model):

    _name = "test.partner.time.window"
    _inherit = "time.window.mixin"
    _description = "Test partner time Window"

    _overlap_check_field = 'partner_id'

    partner_id = fields.Many2one(
        "res.partner", required=True, index=True, ondelete='cascade'
    )

    @api.constrains("partner_id")
    def check_window_no_overlaps(self):
        return super().check_window_no_overlaps()

    @api.depends("start", "end", "weekday_ids")
    def _compute_display_name(self):
        for record in self:
            record.display_name = _("{days}: From {start} to {end}").format(
                days=", ".join(record.weekday_ids.mapped("display_name")),
                start=self.float_to_time_repr(record.start),
                end=self.float_to_time_repr(record.end),
            )

    @api.model
    def float_to_time_repr(self, value):
        pattern = "%02d:%02d"
        hour = math.floor(value)
        min = round((value % 1) * 60)
        if min == 60:
            min = 0
            hour += 1

        return pattern % (hour, min)
