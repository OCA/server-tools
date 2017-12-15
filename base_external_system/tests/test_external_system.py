# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import UserError, ValidationError

from .common import Common


class TestExternalSystem(Common):

    def setUp(self):
        super(TestExternalSystem, self).setUp()
        self.record = self.env.ref('base_external_system.external_system_os')

    def test_get_system_types(self):
        """It should return at least the test record's interface."""
        self.assertIn(
            (self.record._name, self.record._description),
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
        with self._mock_method('client', self.record) as magic:
            with self.record.system_id.client() as client:
                self.assertEqual(client, magic().__enter__())

    def test_create_creates_and_assigns_interface(self):
        """It should create and assign the interface on record create."""
        record = self.env['external.system'].create({
            'name': 'Test',
            'system_type': 'external.system.os',
        })
        self.assertEqual(
            record.interface._name, 'external.system.os',
        )

    def test_create_context_override(self):
        """It should allow for interface create override with context."""
        model = self.env['external.system'].with_context(
            no_create_interface=True,
        )
        record = model.create({
            'name': 'Test',
            'system_type': 'external.system.os',
        })
        self.assertFalse(record.interface)

    def test_action_test_connection(self):
        """It should proxy to the interface connection tester."""
        with self.assertRaises(UserError):
            self.record.system_id.action_test_connection()

    def test_unlink_deletes_interface(self):
        """It should delete the interface when the system is deleted."""
        interface = self.record.interface
        self.assertTrue(interface.exists())
        self.record.unlink()
        self.assertFalse(interface.exists())
