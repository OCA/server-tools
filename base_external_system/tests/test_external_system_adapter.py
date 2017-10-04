# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import UserError

from .common import Common


class TestExternalSystemAdapter(Common):

    def setUp(self):
        super(TestExternalSystemAdapter, self).setUp()
        self.system = self.env.ref('base_external_system.external_system_os')
        self.record = self.env['external.system.adapter'].new({
            'system_id': self.system.id,
        })

    def test_client_yields_client(self):
        """It should yield the client."""
        with self._mock_method('external_get_client') as magic:
            with self.record.client() as client:
                self.assertEqual(client, magic())

    def test_client_destroys_client(self):
        """It should destroy the client after use."""
        with self._mock_method('external_destroy_client') as magic:
            with self.record.client() as client:
                self.assertFalse(magic.call_count)
            magic.assert_called_once_with(client)

    def test_external_get_client_ensure_one(self):
        """It should assert singletons."""
        with self.assertRaises(ValueError):
            self.env['external.system.adapter'].external_get_client()

    def test_external_destroy_client_ensure_one(self):
        """It should assert singletons."""
        with self.assertRaises(ValueError):
            self.env['external.system.adapter'].external_destroy_client(None)

    def test_external_test_connection(self):
        """It should raise a UserError."""
        with self.assertRaises(UserError):
            self.record.external_test_connection()
