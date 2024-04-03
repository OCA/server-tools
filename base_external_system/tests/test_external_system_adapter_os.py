# Copyright 2017 LasLabs Inc.
# Copyright 2023 Therp BV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestExternalSystemAdapterOs(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Remember the working dir, just in case."""
        super(TestExternalSystemAdapterOs, cls).setUpClass()
        cls.working_dir = os.getcwd()

    @classmethod
    def tearDownClass(cls):
        """Set the working dir back to origin, just in case."""
        super(TestExternalSystemAdapterOs, cls).tearDownClass()
        os.chdir(cls.working_dir)

    def setUp(self):
        super(TestExternalSystemAdapterOs, self).setUp()
        self.record = self.env.ref("base_external_system.external_system_os_demo")

    def test_external_system_adapter_os(self):
        """Client should be os, change directory and on destroy restore directory."""
        with self.record.client() as client:
            self.assertEqual(client, os)
            self.assertEqual(os.getcwd(), self.record.remote_path)
        self.assertEqual(os.getcwd(), self.working_dir)

    def test_external_system_adapter_os_test_connection(self):
        """Test testing connections.

        Connecting to existing generally available directory should work.

        Connection to non-existing (or non authorized) directory should
        result in ValidationError.
        """
        self.assertEqual(True, self.record.action_test_connection())
        self.record.remote_path = "/does_not_exist_never_heard_from_666"
        with self.assertRaises(ValidationError):
            self.record.action_test_connection()
