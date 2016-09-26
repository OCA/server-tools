# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
from openerp.http import WebRequest, JsonRequest, request
from openerp.addons.web.controllers import main as web_main
from openerp import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def _authenticate(self, auth_method='user'):
        if request.httprequest.authorization and not request.session.uid:
            request.session.authenticate(
                request.session.db,
                request.httprequest.authorization.username,
                request.httprequest.authorization.password)
        return super(IrHttp, self)._authenticate(auth_method=auth_method)


old_dispatch = JsonRequest.dispatch

def dispatch(self):
    response = old_dispatch(self)
    if self.endpoint.method.im_func == web_main.Session.destroy.im_func:
        response.status = '301 logout'
        response.headers.add(
            'Location',
            self.httprequest.url.replace('://', '://logout@'))
    return response

JsonRequest.dispatch = dispatch
