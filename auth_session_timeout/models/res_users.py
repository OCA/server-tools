# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D, Jesse Morgan

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

    def _auth_timeout_urls_get(self, session, db, uid):
        # Pluggable method for calculating ignored urls
        # Defaults to stored config param
        param_obj = self.pool['ir.config_parameter']
        return param_obj._auth_timeout_get_parameter_urls(db)

    def _auth_timeout_deadline_calculate(self, session, db, uid):
        # Pluggable method for calculating timeout deadline
        # Defaults to current time minus delay using delay stored as session param
        param_obj = self.pool['ir.config_parameter']
        delay = param_obj._auth_timeout_get_parameter_delay(db)
        if delay == False or delay <= 0:
            return False
        return time() - delay

    def _auth_timeout_session_validity_check(self, db, uid, passwd):
        if not request:
            return

        session = request.session

        # Calculate Deadline DateTime
        deadline = self._auth_timeout_deadline_calculate(session, db, uid)

        # Check if deadline expired
        expired = False
        if deadline != False:
            path = root.session_store.get_session_filename(session.sid)
            try:
                expired = getmtime(path) < deadline
            except OSError:
                pass

        # Try to expire the session
        if expired:
            expired = self._auth_timeout_session_expire(session, db, uid)

        # If not aborted, all done.
        if expired:
            return
        
        # Otherwise, fetch urls to ignore
        urls = self._auth_timeout_urls_get(session, db, uid)

        # Update session last modified and access times
        if http.request.httprequest.path not in urls:
            try:
                utime(path, None)
            except OSError:
                pass
                
        return

    def _auth_timeout_session_expire(self, session, db, uid):
        # Pluggable method for enacting logout on an expired session
        # Returns True if session is timed out/expired
        # This is a late stage where a timeout can be aborted.
        # Useful if you want to do some heavy checking, as it won't be
        # called unless the session inactivity deadline has been reached
        if session.db and session.uid:
            session.logout(keep_db=True)
        return True

    def check(self, db, uid, passwd):
        res = super(ResUsers, self).check(db, uid, passwd)
        self._auth_timeout_session_validity_check(db, uid, passwd)
        return res
