# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    time_window_ids = fields.One2many(
        comodel_name="test.partner.time.window",
        inverse_name="partner_id",
        string="Time windows",
    )

    def get_delivery_windows(self, day_name):
        """
        Return the list of delivery windows by partner id for the given day

        :param day: The day name (see time.weekday, ex: 0,1,2,...)
        :return: dict partner_id:[time_window_ids, ]
        """
        weekday_id = self.env["time.weekday"]._get_id_by_name(day_name)
        res = defaultdict(list)
        windows = self.env["test.partner.time.window"].search(
            [
                ("partner_id", "in", self.ids),
                ("time_window_weekday_ids", "in", weekday_id)
            ]
        )
        for window in windows:
            res[window.partner_id.id].append(window)
        return res
