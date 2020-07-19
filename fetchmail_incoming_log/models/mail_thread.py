# Copyright 2017-20 ForgeFlow S.L. (www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import email
import logging
import xmlrpc.client as xmlrpclib

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_process(
        self,
        model,
        message,
        custom_values=None,
        save_original=False,
        strip_attachments=False,
        thread_id=None,
    ):
        message_copy = message
        if isinstance(message, xmlrpclib.Binary):
            message = bytes(message.data)
        if isinstance(message, str):
            message = message.encode("utf-8")
        message = email.message_from_bytes(message)
        msg_dict = self.message_parse(message, save_original=save_original)
        _logger.info(
            "Fetched mail from %s to %s with Message-Id %s",
            msg_dict.get("from"),
            msg_dict.get("to"),
            msg_dict.get("message_id"),
        )

        return super(MailThread, self).message_process(
            model,
            message_copy,
            custom_values=custom_values,
            save_original=save_original,
            strip_attachments=strip_attachments,
            thread_id=thread_id,
        )
