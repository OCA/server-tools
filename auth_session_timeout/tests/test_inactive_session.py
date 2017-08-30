# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.tests import common
from ..models.res_users import DELAY_KEY, IGNORED_PATH_KEY
import time


class TestInactiveSession(common.HttpCase):

    def setUp(self):
        super(TestInactiveSession, self).setUp()
        with self.registry.cursor() as test_cursor:
            env = self.env(test_cursor)
            self.ipm = env['ir.config_parameter']
            self.rus = env['res.users']
        self.db = common.get_db_name()

    def test_01_deadline(self):
        """ Test timeout calculation """
        self.ipm.set_param(DELAY_KEY, 1)
        timeout = 1.1
        time_1 = self.rus._auth_timeout_deadline_calculate()
        time.sleep(timeout)
        time_2 = self.rus._auth_timeout_deadline_calculate()
        self.assertAlmostEqual((time_2 - time_1), timeout, places=1)
        self.ipm.set_param(DELAY_KEY, -1)
        self.assertFalse(self.rus._auth_timeout_deadline_calculate())
        self.ipm.set_param(DELAY_KEY, False)
        self.assertFalse(self.rus._auth_timeout_deadline_calculate())

    def test_02_urls(self):
        """ Test logout method """
        self.ipm.set_param(IGNORED_PATH_KEY, False)
        self.assertEqual(self.rus._auth_timeout_ignoredurls_get(), [])
        url_1 = '/calendar/notify'
        url_2 = '/longpolling/poll'
        urls = url_1 + ',' + url_2
        self.ipm.set_param(IGNORED_PATH_KEY, urls)
        urls = self.rus._auth_timeout_ignoredurls_get()
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0], url_1)
        self.assertEqual(urls[1], url_2)

    def test_03_logout(self):
        """ Test logout method """
        self.assertTrue(self.rus._auth_timeout_session_terminate(self.session))
