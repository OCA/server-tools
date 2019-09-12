# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TestOnchangeHelperMessage(models.Model):

    _name = "test_onchange_helper.message"
    _description = "Test Onchange Helper Message"

    discussion = fields.Many2one(
        "test_onchange_helper.discussion", ondelete="cascade"
    )
    body = fields.Text()
    author = fields.Many2one("res.users", default=lambda self: self.env.user)
    name = fields.Char(string="Title", compute="_compute_name", store=True)
    display_name = fields.Char(
        string="Abstract", compute="_compute_display_name"
    )
    discussion_name = fields.Char(
        related="discussion.name", string="Discussion Name"
    )
    author_partner = fields.Many2one(
        "res.partner",
        compute="_compute_author_partner",
        search="_search_author_partner",
    )
    important = fields.Boolean()

    @api.one
    @api.depends("author.name", "discussion.name")
    def _compute_name(self):
        self.name = "[%s] %s" % (
            self.discussion.name or "",
            self.author.name or "",
        )

    @api.one
    @api.depends("author.name", "discussion.name", "body")
    def _compute_display_name(self):
        stuff = "[%s] %s: %s" % (
            self.author.name,
            self.discussion.name or "",
            self.body or "",
        )
        self.display_name = stuff[:80]

    @api.one
    @api.depends("author", "author.partner_id")
    def _compute_author_partner(self):
        self.author_partner = self.author.partner_id

    @api.model
    def _search_author_partner(self, operator, value):
        return [("author.partner_id", operator, value)]
