# -*- coding: utf-8 -*-
# Copyright 2023 Therp BV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestExternalSystem(TransactionCase):
    def setUp(self):
        super(TestExternalSystem, self).setUp()
        self.record = self.env.ref("base_external_system_http.external_system_github")

    def test_get_system_types(self):
        """It should return at least the test record's interface."""
        system_type_http = self.env["external.system.adapter.http"]
        self.assertIn(
            (system_type_http._name, system_type_http._description),
            self.env["external.system"]._get_system_types(),
        )

    def test_client(self):
        """The client should be the adapter class."""
        system_type_http = self.env["external.system.adapter.http"]
        with self.record.client() as client:
            self.assertEqual(client, system_type_http)
            # Client should have system_id property.
            self.assertEqual(client.system_id, self.record)

    def test_get_http(self):
        """We should be able to get response from system."""
        with self.record.client() as client:
            response = client.get()
            self.assertIn("<head", response.text)

    def test_get_http_endpoint(self):
        """We should be able to get response from system."""
        with self.record.client() as client:
            response = client.get(endpoint="tools")
            self.assertIn("server-tools", response.text)

    def test_action_test_connection(self):
        """It should correctly connect to the remote system."""
        self.record.action_test_connection()
