# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D

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
        delay, urls = self.param_obj.get_session_parameters(self.db)
        self.assertEqual(delay, int(self.delay.value))
        self.assertIsInstance(delay, int)
        self.assertIsInstance(urls, list)
