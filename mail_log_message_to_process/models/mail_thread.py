# -*- coding: utf-8 -*-
# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#           (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import email
import xmlrpclib
import logging
from email.message import Message
from odoo import api, models
from odoo.tools import decode_smtp_header as decode

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_parse_basic_data(self, message):
        """Parses a string or email.message.Message representing an RFC-2822
        email, and returns a generic dict holding the message details.

        :param message: the message to parse
        :rtype: dict
        :return: A dict with the following structure, where each field
        may not be present if missing in original message:
            { 'message_id': msg_id,
              'subject': subject,
              'from': from,
              'to': to,
              'cc': cc
            }
        """

        msg_dict = {
            'message_type': 'email',
        }
        if not isinstance(message, Message):
            if isinstance(message, unicode):
                # Warning: message_from_string doesn't always work
                # correctly on unicode, we must use utf-8 strings here :-(
                message = message.encode('utf-8')
            message = email.message_from_string(message)

        message_id = message['message-id']
        if not message_id:
            message_id = 'None'
        msg_dict['message_id'] = message_id
        if message.get('Subject'):
            msg_dict['subject'] = decode(message.get('Subject'))

        # Envelope fields not stored in mail.message but made available
        # for message_new()
        msg_dict['from'] = decode(message.get('from'))
        msg_dict['to'] = decode(message.get('to'))
        msg_dict['cc'] = decode(message.get('cc'))
        msg_dict['email_from'] = decode(message.get('from'))
        return msg_dict

    @api.model
    def message_process(self, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None):

        if isinstance(message, xmlrpclib.Binary):
            message = str(message.data)
        # Warning: message_from_string doesn't always work correctly on
        # unicode, we must use utf-8 strings here :-(
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        msg_txt = email.message_from_string(message)
        msg = self.message_parse_basic_data(msg_txt)
        _logger.info(
            'Fetched mail from %s to %s with Message-Id %s',
            msg.get('from'), msg.get('to'), msg.get('message_id'))

        return super(MailThread, self).message_process(
            model, message, custom_values=custom_values,
            save_original=save_original,
            strip_attachments=strip_attachments, thread_id=thread_id)
