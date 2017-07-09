# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import models

from openerp.http import root
from openerp.http import request

from os import utime
from os.path import getmtime
from time import time

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _auth_timeout_ignoredurls_get(self):
        """Pluggable method for calculating ignored urls
        Defaults to stored config param
        """
        param_model = self.pool['ir.config_parameter']
        return param_model._auth_timeout_get_parameter_ignoredurls()

    def _auth_timeout_deadline_calculate(self):
        """Pluggable method for calculating timeout deadline
        Defaults to current time minus delay using delay stored as config param
        """
        param_model = self.pool['ir.config_parameter']
        delay = param_model._auth_timeout_get_parameter_delay()
        if delay is False or delay <= 0:
            return False
        return time() - delay

    def _auth_timeout_session_terminate(self, session):
        """Pluggable method for terminating a timed-out session

        This is a late stage where a session timeout can be aborted.
        Useful if you want to do some heavy checking, as it won't be
        called unless the session inactivity deadline has been reached.

        Return:
            True: session terminated
            False: session timeout cancelled
        """
        if session.db and session.uid:
            session.logout(keep_db=True)
        return True

    def _auth_timeout_request_get(self):
        return request

    def _auth_timeout_session_filename_get(self, sid):
        return root.session_store.get_session_filename(sid)

    def _auth_timeout_utime(self, path, dates=None):
        return utime(path, dates)

    def _auth_timeout_getmtime(self, path):
        return getmtime(path)

    def _auth_timeout_check(self):
        _request = self._auth_timeout_request_get()

        if not _request:
            return

        session = _request.session

        # Calculate deadline
        deadline = self._auth_timeout_deadline_calculate()

        # Check if past deadline
        expired = False
        if deadline is not False:
            path = self._auth_timeout_session_filename_get(session.sid)
            try:
                expired = self._auth_timeout_getmtime(path) < deadline
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

        if _request.httprequest.path not in ignoredurls:
            if 'path' not in locals():
                path = self._auth_timeout_session_filename_get(session.sid)
            try:
                self._auth_timeout_utime(path, None)
            except OSError as e:
                _logger.warning(
                    'Exception updating session file access/modified times: %s'
                    % e
                )
                pass

        return

    def _check_session_validity(self, db, uid, passwd):
        """Adaptor method for backward compatibility"""
        return self._auth_timeout_check()

    def check(self, db, uid, passwd):
        res = super(ResUsers, self).check(db, uid, passwd)
        self._check_session_validity(db, uid, passwd)
        return res
