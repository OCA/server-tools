# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestIrConfigParameter(TransactionCase):

    def setUp(self):
        super(TestIrConfigParameter, self).setUp()
        self.param_obj = self.env['ir.config_parameter']
        self.data_obj = self.env['ir.model.data']
        self.delay = self.env.ref(
            'auth_session_timeout.inactive_session_time_out_delay'
        )
        self.url = self.env.ref(
            'auth_session_timeout.inactive_session_time_out_ignored_url'
        )
        self.urls = ['url1', 'url2']
        self.url.value = ','.join(self.urls)

    def test_get_session_parameters_delay(self):
        """ It should return the proper delay """
        delay, _ = self.param_obj.get_session_parameters()
        self.assertEqual(delay, int(self.delay.value))

    def test_get_session_parameters_url(self):
        """ It should return URIs split by comma """
        _, urls = self.param_obj.get_session_parameters()
        self.assertEqual(urls, self.urls)
