# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import math

from odoo import _, api, fields, models


class TestPartnerTimeWindow(models.Model):

    _name = "test.partner.time.window"
    _inherit = "time.window.mixin"
    _description = "Test partner time Window"

    _time_window_overlap_check_field = "partner_id"

    partner_id = fields.Many2one(
        "res.partner", required=True, index=True, ondelete='cascade'
    )

    @api.constrains("partner_id")
    def check_window_no_overlaps(self):
        return super().check_window_no_overlaps()
