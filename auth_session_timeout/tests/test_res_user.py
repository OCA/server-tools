# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from time import time

from openerp.tests import common


class MockOpenerpSession():
    uid = 1
    db = 'test'
    sid = 123
    loggedout = False

    def logout(self, keep_db):
        self.loggedout = True


class MockRequest():
    path = 'test'


class MockOpenerpHttpHttpRequest():
    session = MockOpenerpSession()
    httprequest = MockRequest()


class TestSessionExpiry(common.TransactionCase):
    def setUp(self):
        super(TestSessionExpiry, self).setUp()
        self.resusers_obj = self.env['res.users']
        self.request = MockOpenerpHttpHttpRequest()

        def _auth_timeout_deadline_calculate(*args, **kwargs):
            return time()

        self.resusers_obj._patch_method(
            '_auth_timeout_deadline_calculate',
            _auth_timeout_deadline_calculate)

        def _auth_timeout_request_get(*args, **kwargs):
            return self.request

        self.resusers_obj._patch_method(
            '_auth_timeout_request_get',
            _auth_timeout_request_get)

        def _auth_timeout_session_filename_get(*args, **kwargs):
            return 'non-existent-filename'

        self.resusers_obj._patch_method(
            '_auth_timeout_session_filename_get',
            _auth_timeout_session_filename_get)

        def _auth_timeout_getmtime(*args, **kwargs):
            return time() - 61

        self.resusers_obj._patch_method(
            '_auth_timeout_getmtime',
            _auth_timeout_getmtime)

    def tearDown(self):
        super(TestSessionExpiry, self).tearDown()
        self.resusers_obj._revert_method('_auth_timeout_deadline_calculate')
        self.resusers_obj._revert_method('_auth_timeout_request_get')
        self.resusers_obj._revert_method('_auth_timeout_session_filename_get')
        self.resusers_obj._revert_method('_auth_timeout_getmtime')

    def test_check_timedout_session_loggedout(self):
        self.resusers_obj._auth_timeout_check()
        self.assertEquals(self.request.session.loggedout, True)


class TestSessionFileReadWriteException(common.TransactionCase):
    def setUp(self):
        super(TestSessionFileReadWriteException, self).setUp()
        self.resusers_obj = self.env['res.users']

        def _auth_timeout_request_get(*args, **kwargs):
            return MockOpenerpHttpHttpRequest()

        self.resusers_obj._patch_method(
            '_auth_timeout_request_get',
            _auth_timeout_request_get)

        def _auth_timeout_session_filename_get(*args, **kwargs):
            return 'non-existent-filename'

        self.resusers_obj._patch_method(
            '_auth_timeout_session_filename_get',
            _auth_timeout_session_filename_get)

    def tearDown(self):
        super(TestSessionFileReadWriteException, self).tearDown()
        self.resusers_obj._revert_method('_auth_timeout_request_get')
        self.resusers_obj._revert_method('_auth_timeout_session_filename_get')

    def test_check_sessionfile_time_readwrite_exception(self):
        self.resusers_obj._auth_timeout_check()
