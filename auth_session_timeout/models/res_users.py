# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE - Cédric Pigeon
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, http, models
from odoo.http import request, root

from os import utime
from os.path import getmtime
from time import time

DELAY_KEY = 'inactive_session_time_out_delay'
IGNORED_PATH_KEY = 'inactive_session_time_out_ignored_url'


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _auth_timeout_urls_get(self):
        """
        Pluggable method for calculating ignored urls.     
        :return: ignored urls
        """
        urls = self.env['ir.config_parameter'].get_param(IGNORED_PATH_KEY)
        return (urls.split(',') if urls else [])

    def _auth_timeout_session_expire(self, session):
        """
        Pluggable method for enacting logout on an expired session. This is a 
        late stage where a timeout can be aborted. Useful if you want to do 
        some heavy checking, as it won't be called unless the session 
        inactivity deadline has been reached.
        :param session: 
        :return: True if session is timed out/expired.
        """
        if session.db and session.uid:
            session.logout(keep_db=True)
        return True

    def _auth_timeout_deadline_calculate(self):
        """
        Pluggable method for calculating timeout deadline. Defaults to current 
        time minus delay using delay stored as session param.
        :param session: 
        :return: calculated delay 
        """
        delay = self.env['ir.config_parameter'].get_param(DELAY_KEY)
        delay = (int(delay) if delay else False)
        if not delay or delay < 0:
            return False
        return time() - delay

    @api.model
    def _check_session_validity(self):
        if not request:
            return
        session = request.session
        session_store = root.session_store
        urls = self._auth_timeout_urls_get()
        deadline = self._auth_timeout_deadline_calculate()
        path = session_store.get_session_filename(session.sid)
        try:
            if any(map(http.request.httprequest.path.startswith, urls)):
                return
            if getmtime(path) < deadline:
                self._auth_timeout_session_expire(session)
            else:
                utime(path, None)
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
