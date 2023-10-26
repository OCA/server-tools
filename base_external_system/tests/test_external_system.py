# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2023 Therp BV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import os

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestExternalSystem(TransactionCase):

    def setUp(self):
        super(TestExternalSystem, self).setUp()
        self.record = self.env.ref('base_external_system.external_system_os_demo')

    def test_get_system_types(self):
        """It should return at least the test record's interface."""
        system_type_os = self.env["external.system.os"]
        self.assertIn(
            (system_type_os._name, system_type_os._description),
            self.env['external.system']._get_system_types(),
        )

    def test_check_fingerprint_blank(self):
        """It should not allow blank fingerprints when checking enabled."""
        with self.assertRaises(ValidationError):
            self.record.write({
                'ignore_fingerprint': False,
                'fingerprint': False,
            })

    def test_check_fingerprint_allowed(self):
        """It should not raise a validation error if there is a fingerprint."""
        self.record.write({
            'ignore_fingerprint': False,
            'fingerprint': 'Data',
        })
        self.assertTrue(True)

    def test_client(self):
        """It should yield the open interface client."""
        with self.record.client() as client:
            self.assertEqual(client, os)

    def test_action_test_connection(self):
        """It should proxy to the interface connection tester."""
        self.record.action_test_connection()
