# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TestOnchangeHelperMultiLine(models.Model):

    _name = "test_onchange_helper.multi.line"
    _description = "Test Onchange Helper Multi Line"

    multi = fields.Many2one("test_onchange_helper.multi", ondelete="cascade")
    name = fields.Char()
    partner = fields.Many2one("res.partner")
