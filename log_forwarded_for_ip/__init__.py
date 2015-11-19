# -*- coding: utf-8 -*-
# © 2015 Aserti Global Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from werkzeug.serving import WSGIRequestHandler


def address_string(self):
    forwarded_for = self.headers.get('X-Forwarded-For', '').split(',')
    if forwarded_for and forwarded_for[0]:
        return forwarded_for[0]
    else:
        return self.client_address[0]

WSGIRequestHandler.address_string = address_string
