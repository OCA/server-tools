# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import \
    serialize_exception, content_disposition


class Dbf2csvController(http.Controller):
    @http.route('/web/binary/download_document', type='http', auth="public")
    @serialize_exception
    def download_document(self, filename, **kw):
        with open('/tmp/' + filename) as f:
            filecontent = f.read() + '\n'
        return request.make_response(
            filecontent,
            [('Content-Type', 'application/octet-stream'),
             ('Content-Disposition', content_disposition(filename))])
