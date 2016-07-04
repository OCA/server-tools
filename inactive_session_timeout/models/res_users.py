# -*- coding: utf-8 -*-
##############################################################################

#     This file is part of inactive_session_timeout, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     inactive_session_timeout is free software: you can redistribute it
#     and/or modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     inactive_session_timeout is distributed in the hope that it will
#     be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with inactive_session_timeout.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models
from openerp import http

from openerp.http import root
from openerp.http import request

from os import utime
from os.path import getmtime
from time import time


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _check_session_validity(self, db, uid, passwd):
        if not request:
            return
        session = request.session
        session_store = root.session_store
        param_obj = self.pool['ir.config_parameter']
        delay, urls = param_obj.get_session_parameters(db)
        deadline = time() - delay
        path = session_store.get_session_filename(session.sid)
        try:
            if getmtime(path) < deadline:
                if session.db and session.uid:
                    session.logout(keep_db=True)
            elif http.request.httprequest.path not in urls:
                # the session is not expired, update the last modification
                # and access time.
                utime(path, None)
        except OSError:
            pass
        return

    def check(self, db, uid, passwd):
        res = super(ResUsers, self).check(db, uid, passwd)
        self._check_session_validity(db, uid, passwd)
        return res
