# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TestOnchangeHelperDiscussion(models.Model):

    _name = "test_onchange_helper.discussion"
    _description = "Test Onchange Helper Discussion"

    name = fields.Char(
        string="Title",
        required=True,
        help="General description of what this discussion is about.",
    )
    moderator = fields.Many2one("res.users")
    categories = fields.Many2many(
        "test_onchange_helper.category",
        "test_onchange_helper_discussion_category",
        "discussion",
        "category",
    )
    participants = fields.Many2many("res.users")
    messages = fields.One2many("test_onchange_helper.message", "discussion")
    message_concat = fields.Text(string="Message concatenate")
    important_messages = fields.One2many(
        "test_onchange_helper.message",
        "discussion",
        domain=[("important", "=", True)],
    )
    very_important_messages = fields.One2many(
        "test_onchange_helper.message",
        "discussion",
        domain=lambda self: self._domain_very_important(),
    )
    emails = fields.One2many("test_onchange_helper.emailmessage", "discussion")
    important_emails = fields.One2many(
        "test_onchange_helper.emailmessage",
        "discussion",
        domain=[("important", "=", True)],
    )

    def _domain_very_important(self):
        """Ensure computed O2M domains work as expected."""
        return [("important", "=", True)]

    @api.onchange("name")
    def _onchange_name(self):
        # test onchange modifying one2many field values
        # update body of existings messages and emails
        for message in self.messages:
            message.body = "not last dummy message"
        for message in self.important_messages:
            message.body = "not last dummy message"
        # add new dummy message
        message_vals = self.messages._add_missing_default_values(
            {"body": "dummy message", "important": True}
        )
        self.messages |= self.messages.new(message_vals)
        self.important_messages |= self.messages.new(message_vals)

    @api.onchange("moderator")
    def _onchange_moderator(self):
        self.participants |= self.moderator

    @api.onchange("messages")
    def _onchange_messages(self):
        self.message_concat = "\n".join(
            ["%s:%s" % (m.name, m.body) for m in self.messages]
        )
