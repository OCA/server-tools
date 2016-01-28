# -*- coding: utf-8 -*-
# © 2015 Aserti Global Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from werkzeug.serving import WSGIRequestHandler
from mimetools import Message
from openerp import models


def address_string(self):
    if self.headers and isinstance(self.headers, Message):
        forwarded_for = self.headers.get('X-Forwarded-For', '').split(',')
        if forwarded_for and forwarded_for[0]:
            return forwarded_for[0]
    return self.client_address[0]


class LogForwardedForIpInstalled(models.AbstractModel):
    _name = 'log.forwarded.for.ip.installed'

    def _register_hook(self, cr):
        if not hasattr(WSGIRequestHandler, '_address_string_org'):
            WSGIRequestHandler._address_string_org = \
                WSGIRequestHandler.address_string
            WSGIRequestHandler.address_string = address_string
        return super(LogForwardedForIpInstalled, self)._register_hook(cr)
