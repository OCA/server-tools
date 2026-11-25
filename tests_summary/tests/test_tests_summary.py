# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os
from unittest import expectedFailure

from odoo.tests.common import SavepointCase

if os.getenv("RUN_TESTS_SUMMARY_TESTS"):

    class TestTestsSummary(SavepointCase):
        def test_tests_summary_ok(self):
            self.assertTrue(True)

        def test_tests_summary_fail(self):
            self.assertTrue(False)

        def test_tests_summary_error(self):
            raise Exception("Error")

        def test_tests_summary_skip(self):
            self.skipTest("Skip")

        @expectedFailure
        def test_tests_summary_expected_failure(self):
            raise Exception("XFail")

        @expectedFailure
        def test_tests_summary_unexpected_success(self):
            self.assertTrue(True)
