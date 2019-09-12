# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TestOnchangeHelperMulti(models.Model):

    _name = "test_onchange_helper.multi"
    _description = "Test Onchange Helper Multi"

    name = fields.Char(related="partner.name", readonly=True)
    partner = fields.Many2one("res.partner")
    lines = fields.One2many("test_onchange_helper.multi.line", "multi")

    @api.onchange("name")
    def _onchange_name(self):
        for line in self.lines:
            line.name = self.name

    @api.onchange("partner")
    def _onchange_partner(self):
        for line in self.lines:
            line.partner = self.partner
