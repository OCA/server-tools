# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os

from odoo.tests.common import TransactionCase


class TestExternalSystemOs(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Remember the working dir, just in case."""
        super(TestExternalSystemOs, cls).setUpClass()
        cls.working_dir = os.getcwd()

    @classmethod
    def tearDownClass(cls):
        """Set the working dir back to origin, just in case."""
        super(TestExternalSystemOs, cls).tearDownClass()
        os.chdir(cls.working_dir)

    def setUp(self):
        super(TestExternalSystemOs, self).setUp()
        self.record = self.env.ref('base_external_system.external_system_os_demo')

    def test_external_system_os(self):
        """Client should be os, change directory and on destroy restore directory."""
        with self.record.client() as client:
            self.assertEqual(client, os)
            self.assertEqual(os.getcwd(), self.record.remote_path)
        self.assertEqual(os.getcwd(), self.working_dir)
