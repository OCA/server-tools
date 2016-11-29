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
from odoo.http import WebRequest, JsonRequest
from openerp.addons.web.controllers import main as web_main

old_init = WebRequest.init


def init(self, params):
    old_init(self, params)
    if self.httprequest.authorization and not self.session._login:
        dbs = web_main.db_list(self)
        self.session.authenticate(
            dbs and dbs[0],
            self.httprequest.authorization.username,
            self.httprequest.authorization.password,
            dict(
                base_location=self.httprequest.url_root.rstrip('/'),
                HTTP_HOST=self.httprequest.environ['HTTP_HOST'],
                REMOTE_ADDR=self.httprequest.environ['REMOTE_ADDR']
            )
        )

WebRequest.init = init

old_dispatch = JsonRequest.dispatch


def dispatch(self, method):
    response = old_dispatch(self, method)
    if method.im_func == web_main.Session.destroy.im_func:
        response.status = '301 logout'
        response.headers.add(
            'Location',
            self.httprequest.url.replace('://', '://logout@'))
    return response

JsonRequest.dispatch = dispatch
