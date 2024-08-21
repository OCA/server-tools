# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2023 Therp BV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Check wther calling not implemented methods on abstract class raise exceptions."""

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestExternalSystemAdapter(TransactionCase):
    def setUp(self):
        super(TestExternalSystemAdapter, self).setUp()
        self.abstract_adapter = self.env["external.system.adapter"]

    def test_external_get_client(self):
        """It should raise a UserError."""
        with self.assertRaises(UserError):
            self.abstract_adapter.external_get_client()

    def test_external_destroy_client(self):
        """It should raise a UserError."""
        with self.assertRaises(UserError):
            self.abstract_adapter.external_destroy_client(None)
