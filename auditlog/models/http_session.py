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


class AuditlogtHTTPSession(models.Model):
    _name = 'auditlog.http.session'
    _description = u"Auditlog - HTTP User session log"
    _order = "create_date DESC"

    name = fields.Char(u"Session ID")
    user_id = fields.Many2one(
        'res.users', string=u"User")
    http_request_ids = fields.One2many(
        'auditlog.http.request', 'http_session_id', string=u"HTTP Requests")

    @api.model
    def current_http_session(self):
        """Create a log corresponding to the current HTTP user session, and
        returns its ID. This method can be called several times during the
        HTTP query/response cycle, it will only log the user session on the
        first call.
        If no HTTP user session is available, returns `False`.
        """
        httpsession = request.httpsession
        if httpsession:
            existing_session = self.search(
                [('name', '=', httpsession.sid),
                 ('user_id', '=', request.uid)])
            if existing_session:
                return existing_session.id
            vals = {
                'name': httpsession.sid,
                'user_id': request.uid,
            }
            httpsession.auditlog_http_session_id = self.create(vals).id
            return httpsession.auditlog_http_session_id
        return False
