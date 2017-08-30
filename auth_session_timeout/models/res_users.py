# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE - Cédric Pigeon
# Copyright 2017 Jesse Morgan
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.http import request, root

import logging
from os import utime
from os.path import getmtime
from time import time
_logger = logging.getLogger(__name__)

DELAY_KEY = 'inactive_session_time_out_delay'
IGNORED_PATH_KEY = 'inactive_session_time_out_ignored_url'


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _auth_timeout_ignoredurls_get(self):
        """
        Pluggable method for calculating ignored urls.
        :return: ignored urls
        """
        urls = self.env['ir.config_parameter'].get_param(IGNORED_PATH_KEY)
        return (urls.split(',') if urls else [])

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

    def _auth_timeout_session_terminate(self, session):
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

    @api.model
    def _auth_timeout_check(self):
        if not request:
            return
        session = request.session
        deadline = self._auth_timeout_deadline_calculate()
        expired = False
        if deadline is not False:
            path = root.session_store.get_session_filename(session.sid)
            try:
                expired = getmtime(path) < deadline
            except OSError as e:
                _logger.warning(
                    'Exception reading session file modified time: %s'
                    % e
                )
                pass
        # Try to terminate the session
        terminated = False
        if expired:
            terminated = self._auth_timeout_session_terminate(session)
        # If session terminated, all done
        if terminated:
            return
        # Else, conditionally update session modified and access times
        ignoredurls = self._auth_timeout_ignoredurls_get()
        if request.httprequest.path not in ignoredurls:
            if 'path' not in locals():
                path = root.session_store.get_session_filename(session.sid)
            try:
                utime(path, None)
            except OSError as e:
                _logger.warning(
                    'Exception updating session file access/modified times: %s'
                    % e
                )
                pass
        return

    def _check_session_validity(self):
        """Adaptor method for backward compatibility"""
        return self._auth_timeout_check()

    @classmethod
    def check(cls, db, uid, passwd):
        res = super(ResUsers, cls).check(db, uid, passwd)
        cr = cls.pool.cursor()
        try:
            self = api.Environment(cr, uid, {})[cls._name]
            self._auth_timeout_check()
        finally:
            cr.close()
        return res
