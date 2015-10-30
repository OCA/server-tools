# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ABF OSIELL (<http://osiell.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from openerp.http import request


class AuditlogHTTPRequest(models.Model):
    _name = 'auditlog.http.request'
    _description = u"Auditlog - HTTP request log"
    _order = "create_date DESC"

    name = fields.Char(u"Path")
    root_url = fields.Char(u"Root URL")
    user_id = fields.Many2one(
        'res.users', string=u"User")
    http_session_id = fields.Many2one(
        'auditlog.http.session', string=u"Session")
    user_context = fields.Char(u"Context")
    log_ids = fields.One2many(
        'auditlog.log', 'http_request_id', string=u"Logs")

    @api.model
    def current_http_request(self):
        """Create a log corresponding to the current HTTP request, and returns
        its ID. This method can be called several times during the
        HTTP query/response cycle, it will only log the request on the
        first call.
        If no HTTP request is available, returns `False`.
        """
        http_session_model = self.env['auditlog.http.session']
        httprequest = request.httprequest
        if httprequest:
            if hasattr(httprequest, 'auditlog_http_request_id'):
                return httprequest.auditlog_http_request_id
            vals = {
                'name': httprequest.path,
                'root_url': httprequest.url_root,
                'user_id': request.uid,
                'http_session_id': http_session_model.current_http_session(),
                'user_context': request.context,
            }
            httprequest.auditlog_http_request_id = self.create(vals).id
            return httprequest.auditlog_http_request_id
        return False
