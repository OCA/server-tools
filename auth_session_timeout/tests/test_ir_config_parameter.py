# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import threading
from time import time

from openerp.tests import common
import openerp


class TestIrConfigParameter(common.TransactionCase):

    def setUp(self):
        super(TestIrConfigParameter, self).setUp()
        self.db = openerp.tools.config['db_name']
        if not self.db and hasattr(threading.current_thread(), 'dbname'):
            self.db = threading.current_thread().dbname
        self.param_obj = self.env['ir.config_parameter']
        self.data_obj = self.env['ir.model.data']
        self.delay = self.env.ref(
            'auth_session_timeout.inactive_session_time_out_delay')

    def test_check_session_params(self):
        delay, urls = self.param_obj.get_session_parameters(self.db)
        self.assertEqual(delay, int(self.delay.value))
        self.assertIsInstance(delay, int)
        self.assertIsInstance(urls, list)

    def test_check_session_param_delay(self):
        delay = self.param_obj._auth_timeout_get_parameter_delay()
        self.assertEqual(delay, int(self.delay.value))
        self.assertIsInstance(delay, int)

    def test_check_session_param_urls(self):
        urls = self.param_obj._auth_timeout_get_parameter_ignoredurls()
        self.assertIsInstance(urls, list)


class MockSession():
    uid = 1
    db = 'test'
    sid = 123
    loggedout = False

    def logout(self, keep_db):
        self.loggedout = True

class MockHttpRequest():
    path = 'test'


class MockRequest():
    session = MockSession()
    httprequest = MockHttpRequest()


class TestSessionExpiry(common.TransactionCase):

    def setUp(self):
        super(TestSessionExpiry, self).setUp()
        self.resusers_obj = self.env['res.users']
        self.request = MockRequest()

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
            return MockRequest()
        self.resusers_obj._patch_method(
            '_auth_timeout_request_get',
            _auth_timeout_request_get)

        def _auth_timeout_session_filename_get(*args, **kwargs):
            return 'non-existent-filename'
        self.resusers_obj._patch_method(
            '_auth_timeout_session_filename_get',
            _auth_timeout_session_filename_get)

    def tearDown(self):
        self.resusers_obj._revert_method('_auth_timeout_request_get')
        self.resusers_obj._revert_method('_auth_timeout_session_filename_get')

    def test_check_sessionfile_time_readwrite_exception(self):
        self.resusers_obj._auth_timeout_check()