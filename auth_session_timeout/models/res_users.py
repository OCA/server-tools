# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from os import utime
from os.path import getmtime
from time import time

from odoo import models, http


class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _check_session_validity(cls, db, uid, passwd):
        if not http.request:
            return
        session = http.request.session
        session_store = http.root.session_store
        ConfigParam = http.request.env['ir.config_parameter']
        delay, urls = ConfigParam.get_session_parameters()
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
    def check(cls, db, uid, passwd):
        res = super(ResUsers, cls).check(db, uid, passwd)
        cls._check_session_validity(db, uid, passwd)
        return res
