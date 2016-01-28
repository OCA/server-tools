# -*- coding: utf-8 -*-
# © 2015 Aserti Global Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from werkzeug.serving import WSGIRequestHandler
from openerp import models


class log_forwarded_for_ip_installed(models.AbstractModel):
    _name = 'log.forwarded.for.ip.installed'

address_string_original = WSGIRequestHandler.address_string

def address_string(self):
    if self.pool.get('log.forwarded.for.ip.installed'):
        # Code executed if the module log_forwarded_for_ip is installed
        if self.headers and isinstance(self.headers, dict):
            forwarded_for = self.headers.get('X-Forwarded-For', '').split(',')
            if forwarded_for and forwarded_for[0]:
                return forwarded_for[0]
        return self.client_address[0]
    else:
        # If the module is NOT installed, we execute the original code
        address_string_original(self)
    return True

WSGIRequestHandler.address_string = address_string
