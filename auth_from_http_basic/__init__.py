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
from openerp.addons.web.http import WebRequest
from openerp.addons.web.controllers.main import db_list

old_init = WebRequest.init

def init(self, params):
    old_init(self, params)
    if self.httprequest.authorization and not self.session._login:
        dbs = db_list(self)
        self.session.authenticate(
                dbs and dbs[0],
                self.httprequest.authorization.username,
                self.httprequest.authorization.password,
                dict(
                    base_location=self.httprequest.url_root.rstrip('/'),
                    HTTP_HOST=self.httprequest.environ['HTTP_HOST'],
                    REMOTE_ADDR=self.httprequest.environ['REMOTE_ADDR']
                    ))

WebRequest.init = init
