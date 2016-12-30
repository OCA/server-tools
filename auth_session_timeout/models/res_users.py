# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
