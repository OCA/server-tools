# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE - Cédric Pigeon
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, http, models
from odoo.http import request, root

from os.path import getmtime
from time import time

DELAY_KEY = 'inactive_session_time_out_delay'
IGNORED_PATH_KEY = 'inactive_session_time_out_ignored_url'


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _check_session_validity(self):
        if not request:
            return
        session = request.session
        session_store = root.session_store
        ipm = self.env['ir.config_parameter']
        delay = ipm.get_param(DELAY_KEY, 7200)
        delay = (int(delay) if delay else False)
        # Note that get_param is cached
        urls = ipm.get_param(IGNORED_PATH_KEY, '')
        urls = (urls.split(',') if urls else [])
        deadline = time() - delay
        path = session_store.get_session_filename(session.sid)
        try:
            if any([url in http.request.httprequest.path for url in urls]):
                return
            if getmtime(path) < deadline:
                if session.db and session.uid:
                    session.logout(keep_db=True)
        except OSError:
            pass
        return

    @classmethod
    def check(cls, db, uid, passwd):
        res = super(ResUsers, cls).check(db, uid, passwd)
        cr = cls.pool.cursor()
        try:
            self = api.Environment(cr, uid, {})[cls._name]
            self._check_session_validity()
        finally:
            cr.close()
        return res
