# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D, Jesse Morgan

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import threading

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

    def test_check_delay(self):
        delay = self.param_obj._auth_timeout_get_parameter_delay(self.db)
        self.assertEqual(delay, int(self.delay.value))
        self.assertIsInstance(delay, int)

    def test_check_urls(self):
        urls = self.param_obj._auth_timeout_get_parameter_urls(self.db)
        self.assertIsInstance(urls, list)       
