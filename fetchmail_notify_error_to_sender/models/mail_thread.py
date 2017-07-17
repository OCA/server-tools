# -*- coding: utf-8 -*-
# Copyright 2015 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_route_verify(
        self, message, message_dict, route, update_author=True,
            assert_model=True, create_fallback=True, allow_private=False):
        res = ()
        try:
            res = super(MailThread, self).message_route_verify(
                message, message_dict, route,
                update_author=update_author, assert_model=assert_model,
                create_fallback=create_fallback, allow_private=allow_private)
        except ValueError as ve:
            fetchmail_server_id = self.env.context.get('fetchmail_server_id')
            if not fetchmail_server_id:
                raise ve
            fetchmail_server = self.pool['fetchmail.server'].browse(
                fetchmail_server_id)
            if not fetchmail_server.error_notice_template_id:
                raise ve
            self.env.context['sender_message'] = message
            self.env.context['route_exception'] = ve
            self.env['mail.template'].send_mail(
                fetchmail_server.error_notice_template_id.id,
                fetchmail_server.id)
            self.env.context['error_notice_sent'] = True
        return res

    @api.model
    def message_route(
        self, message, message_dict, model=None, thread_id=None,
            custom_values=None):
        res = []
        try:
            res = super(MailThread, self).message_route(
                message, message_dict, model=model,
                thread_id=thread_id, custom_values=custom_values)
        except ValueError as ve:
            if self.env.context.get('error_notice_sent'):
                # avoid raising exception and setting mail message UNSEEN
                return []
            else:
                raise ve
        return res
