# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TestOnchangeHelperEmailmessage(models.Model):

    _name = "test_onchange_helper.emailmessage"
    _description = "Test Onchange Helper Emailmessage"
    _inherits = {"test_onchange_helper.message": "message"}

    message = fields.Many2one(
        "test_onchange_helper.message",
        "Message",
        required=True,
        ondelete="cascade",
    )
    email_to = fields.Char("To")
