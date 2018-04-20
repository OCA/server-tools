# Copyright 2015-2017 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, tools


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None,
                      custom_values=None):
        try:
            res = super(MailThread, self).message_route(
                message, message_dict, model=model, thread_id=thread_id,
                custom_values=custom_values)
        except ValueError as ve:
            fetchmail_server_id = self.env.context.get('fetchmail_server_id')
            print (tools.pycompat.text_type(ve))
            if not fetchmail_server_id:
                raise ve
            fetchmail_server = self.env['fetchmail.server'].with_context({
                'sender_message': message,
                'route_exception': tools.pycompat.text_type(ve),
            }).browse(fetchmail_server_id)
            if not fetchmail_server.error_notice_template_id:
                raise ve
            fetchmail_server.error_notice_template_id.send_mail(
                fetchmail_server.id)
            raise ve
        return res
