# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import JsonExportTestCase


class TestJsonExportEndpoint(JsonExportTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.endpoint = cls.env["json.export.endpoint"].create(
            {
                "name": "Test Endpoint",
                "schema_id": cls.schema.id,
                "route_path": "test-partners",
                "auth_type": "api_key",
                "page_size": 50,
            }
        )

    # -- URL computation tests --

    def test_compute_full_url(self):
        """Data URL is correctly computed."""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        expected = f"{base_url}/api/json_export/test-partners"
        self.assertEqual(self.endpoint.full_url, expected)

    def test_compute_schema_url(self):
        """Schema URL is correctly computed."""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        expected = f"{base_url}/api/json_export/test-partners/schema"
        self.assertEqual(self.endpoint.schema_url, expected)

    def test_compute_url_empty_path(self):
        """Both URLs empty when route_path is not set."""
        endpoint = self.env["json.export.endpoint"].new(
            {
                "name": "No Path",
                "schema_id": self.schema.id,
                "route_path": False,
            }
        )
        endpoint._compute_full_url()
        self.assertFalse(endpoint.full_url)
        self.assertFalse(endpoint.schema_url)

    # -- Route path validation tests --

    def test_route_path_valid(self):
        """Accepts valid route paths."""
        for path in ["products", "my-products", "v1/products", "under_score"]:
            endpoint = self.env["json.export.endpoint"].create(
                {
                    "name": f"Valid {path}",
                    "schema_id": self.schema.id,
                    "route_path": path,
                    "auth_type": "none",
                }
            )
            self.assertTrue(endpoint.id)
            endpoint.unlink()

    def test_route_path_invalid_chars(self):
        """Raises ValidationError for special characters."""
        with self.assertRaises(ValidationError):
            self.env["json.export.endpoint"].create(
                {
                    "name": "Invalid Path",
                    "schema_id": self.schema.id,
                    "route_path": "products?query=1",
                    "auth_type": "none",
                }
            )

    def test_route_path_unique(self):
        """Raises ValidationError for duplicate active paths."""
        with self.assertRaises(ValidationError):
            self.env["json.export.endpoint"].create(
                {
                    "name": "Duplicate",
                    "schema_id": self.schema.id,
                    "route_path": "test-partners",
                    "auth_type": "none",
                }
            )

    def test_route_path_unique_allows_archived(self):
        """Archived endpoint with same path is allowed."""
        self.endpoint.active = False
        # Should not raise
        endpoint2 = self.env["json.export.endpoint"].create(
            {
                "name": "Reuse Path",
                "schema_id": self.schema.id,
                "route_path": "test-partners",
                "auth_type": "none",
            }
        )
        self.assertTrue(endpoint2.id)

    # -- API key tests --

    def test_auto_generate_api_key_on_create(self):
        """API key is auto-generated when auth_type=api_key and no key given."""
        self.assertTrue(self.endpoint.api_key)
        self.assertEqual(len(self.endpoint.api_key), 64)
        self.assertTrue(self.endpoint.api_key_generated_at)

    def test_no_auto_generate_when_key_provided(self):
        """Explicit api_key on create is preserved."""
        endpoint = self.env["json.export.endpoint"].create(
            {
                "name": "Explicit Key",
                "schema_id": self.schema.id,
                "route_path": "explicit-key",
                "auth_type": "api_key",
                "api_key": "my-custom-key-value",
            }
        )
        self.assertEqual(endpoint.api_key, "my-custom-key-value")

    def test_no_auto_generate_for_none_auth(self):
        """No API key generated when auth_type=none."""
        endpoint = self.env["json.export.endpoint"].create(
            {
                "name": "No Auth",
                "schema_id": self.schema.id,
                "route_path": "no-auth-key",
                "auth_type": "none",
            }
        )
        self.assertFalse(endpoint.api_key)

    def test_constraint_api_key_required(self):
        """Cannot save api_key auth with empty key."""
        with self.assertRaises(ValidationError):
            self.endpoint.write({"api_key": False})

    def test_generate_api_key(self):
        """Generates a 64-char hex string with timestamp."""
        self.endpoint.action_generate_api_key()
        self.assertTrue(self.endpoint.api_key)
        self.assertEqual(len(self.endpoint.api_key), 64)
        # Verify it's valid hex
        int(self.endpoint.api_key, 16)
        self.assertTrue(self.endpoint.api_key_generated_at)

    def test_generate_api_key_unique(self):
        """Two generations produce different keys."""
        self.endpoint.action_generate_api_key()
        key1 = self.endpoint.api_key
        self.endpoint.action_generate_api_key()
        key2 = self.endpoint.api_key
        self.assertNotEqual(key1, key2)
