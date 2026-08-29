from odoo.tests import TransactionCase, tagged
from odoo.tools import config


@tagged("post_install", "-at_install")
class TestBaseModelMethods(TransactionCase):
    """Test base model extension methods."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_get_encrypted_fields_returns_list(self):
        """Test _get_encrypted_fields returns a list."""
        partner = self.env["res.partner"].create({"name": "Test"})
        fields = partner._get_encrypted_fields()
        self.assertIsInstance(fields, list)

    def test_get_encrypted_fields_on_model_without_encrypted(self):
        """Test _get_encrypted_fields on model with no encrypted fields."""
        # res.country has no encrypted fields
        country = self.env["res.country"].search([], limit=1)
        if country:
            fields = country._get_encrypted_fields()
            self.assertEqual(fields, [])


@tagged("post_install", "-at_install")
class TestGetUnmaskedValue(TransactionCase):
    """Test get_unmasked_value method."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

        cls.admin_user = cls.env.ref("base.user_admin")

    def test_get_unmasked_value_invalid_field(self):
        """Test error when field doesn't exist."""
        partner = self.env["res.partner"].create({"name": "Test"})
        with self.assertRaises(ValueError) as cm:
            partner.get_unmasked_value("nonexistent_field")
        self.assertIn("does not exist", str(cm.exception))

    def test_get_unmasked_value_non_encrypted_field(self):
        """Test error when field is not encrypted."""
        partner = self.env["res.partner"].create({"name": "Test"})
        with self.assertRaises(ValueError) as cm:
            partner.get_unmasked_value("name")
        self.assertIn("not an encrypted field", str(cm.exception))

    def test_get_unmasked_value_ensure_one(self):
        """Test that get_unmasked_value requires single record."""
        partners = self.env["res.partner"].search([], limit=2)
        if len(partners) >= 2:
            # Should raise on multi-record
            with self.assertRaises(ValueError):
                partners.get_unmasked_value("name")
