# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE - Cédric Pigeon
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http, models, registry, SUPERUSER_ID
from odoo.api import Environment
from odoo.http import request, root

from os import utime
from os.path import getmtime
from time import time


class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _check_session_validity(cls, db, uid, passwd):
        if not request:
            return
        session = request.session
        session_store = root.session_store
        with registry(db).cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            param_obj = env['ir.config_parameter']
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

    @classmethod
    def check(cls, db, uid, passwd):
        res = super(ResUsers, cls).check(db, uid, passwd)
        cls._check_session_validity(db, uid, passwd)
        return res
