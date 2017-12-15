# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os

from .common import Common


class TestExternalSystemOs(Common):

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
        self.record = self.env.ref('base_external_system.external_system_os')

    def test_external_get_client_returns_os(self):
        """It should return the Pyhton OS module."""
        self.assertEqual(self.record.external_get_client(), os)

    def test_external_get_client_changes_directories(self):
        """It should change to the proper directory."""
        self.record.external_get_client()
        self.assertEqual(os.getcwd(), self.record.remote_path)

    def test_external_destroy_client_changes_directory(self):
        """It should change back to the previous working directory."""
        self.record.external_destroy_client(None)
        self.assertEqual(os.getcwd(), self.working_dir)
