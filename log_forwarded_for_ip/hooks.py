# -*- coding: utf-8 -*-
# © 2015 Aserti Global Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from werkzeug.serving import WSGIRequestHandler


def restore_address_string(cr, reg):
    if hasattr(WSGIRequestHandler, '_address_string_org'):
        WSGIRequestHandler.address_string = \
            WSGIRequestHandler._address_string_org
        del WSGIRequestHandler._address_string_org
