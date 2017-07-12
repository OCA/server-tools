# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo import http

from odoo.http import root
from odoo.http import request

from os import utime
from os.path import getmtime
from time import time
from odoo import api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _check_session_validity(cls, db, uid, passwd):
        if not request:
            return
        session = request.session
        session_store = root.session_store
        try:
            with cls.pool.cursor() as cr:
                ICP = api.Environment(cr, uid, {})['ir.config_parameter']
        except Exception:
            _logger.exception(
                "Failed to update web.base.url configuration parameter")

        delay, urls = ICP.get_session_parameters(db, uid)
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

    @classmethod
    def check(self, db, uid, passwd):
        res = super(ResUsers, self).check(db, uid, passwd)
        self._check_session_validity(db, uid, passwd)
        return res
