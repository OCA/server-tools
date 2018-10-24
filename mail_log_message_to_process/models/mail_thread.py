# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#           (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import email
import xmlrpc.client as xmlrpclib
import logging
from odoo import api, models
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_process(self, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None):

        if isinstance(message, xmlrpclib.Binary):
            message = bytes(message.data)
            # message_from_string parses from a *native string*, except
            # apparently sometimes message is ISO-8859-1 binary data or some
            # shit and the straightforward version (pycompat.to_native) won't
            # work right -> always encode message to bytes then use the
            # relevant method depending on ~python version
        if isinstance(message, pycompat.text_type):
            message = message.encode('utf-8')
        extract = getattr(email, 'message_from_bytes',
                          email.message_from_string)
        msg_txt = extract(message)
        msg = self.message_parse(msg_txt)
        _logger.info(
            'Fetched mail from %s to %s with Message-Id %s',
            msg.get('from'), msg.get('to'), msg.get('message_id'))

        return super(MailThread, self).message_process(
            model, message, custom_values=custom_values,
            save_original=save_original,
            strip_attachments=strip_attachments, thread_id=thread_id)
