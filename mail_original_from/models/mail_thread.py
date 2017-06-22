# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, tools


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_parse(self, message, save_original=False):
        msg_dict = super(MailThread, self)\
            .message_parse(message, save_original)
        original_from = tools.decode_smtp_header(
            message.get('X-Original-From')
        )
        if original_from:
            msg_dict['email_from'] = original_from
            msg_dict['from'] = original_from
        return msg_dict

    @api.model
    def message_route_verify(self, message, message_dict, route,
                             update_author=True, assert_model=True,
                             create_fallback=True, allow_private=False,
                             drop_alias=False):

        # here message is an email.message instance
        if message and message.get('X-Original-From'):
            email_from = message.get('X-Original-From')
            message.replace_header('From', email_from)

        return super(MailThread, self).message_route_verify(
            message, message_dict, route,
            update_author=update_author,
            assert_model=assert_model,
            create_fallback=create_fallback,
            allow_private=allow_private,
            drop_alias=drop_alias)
