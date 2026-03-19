# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged
from odoo.tools import config

from ..fields.encrypted import (Encrypted, apply_format, decrypt_value,
                                encrypt_value, is_encrypted_value,
                                strip_format)


@tagged("post_install", "-at_install")
class TestEncryptedFieldBasics(TransactionCase):
    """Test basic encryption/decryption functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure encryption key is configured for tests
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encrypt then decrypt returns original value."""
        original = "sensitive data 123"
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)
        self.assertEqual(decrypted, original)

    def test_encrypt_returns_different_value(self):
        """Test that encrypted value differs from original."""
        original = "my secret"
        encrypted = encrypt_value(original)
        self.assertNotEqual(encrypted, original)

    def test_encrypt_none_returns_none(self):
        """Test that encrypting None returns None."""
        self.assertIsNone(encrypt_value(None))

    def test_decrypt_none_returns_none(self):
        """Test that decrypting None returns None."""
        self.assertIsNone(decrypt_value(None))

    def test_is_encrypted_value_detection(self):
        """Test detection of encrypted values."""
        encrypted = encrypt_value("test")
        self.assertTrue(is_encrypted_value(encrypted))
        self.assertFalse(is_encrypted_value("plain text"))
        self.assertFalse(is_encrypted_value(""))
        self.assertFalse(is_encrypted_value(None))
        self.assertFalse(is_encrypted_value(123))

    def test_encrypted_value_starts_with_ga(self):
        """Test that Fernet tokens start with 'gA' (version byte 0x80)."""
        encrypted = encrypt_value("test")
        self.assertTrue(encrypted.startswith("gA"))

    def test_decrypt_invalid_token_raises(self):
        """Test that decrypting invalid token raises UserError."""
        with self.assertRaises(UserError):
            decrypt_value("not_a_valid_encrypted_token_at_all")


@tagged("post_install", "-at_install")
class TestFormatPatterns(TransactionCase):
    """Test format pattern application and stripping."""

    def test_ssn_format_apply(self):
        """Test SSN formatting."""
        self.assertEqual(apply_format("123456789", "ssn"), "123-45-6789")

    def test_ssn_format_strip(self):
        """Test SSN format stripping."""
        self.assertEqual(strip_format("123-45-6789", "ssn"), "123456789")

    def test_phone_format_apply(self):
        """Test phone formatting."""
        self.assertEqual(apply_format("1234567890", "phone"), "(123) 456-7890")

    def test_phone_format_strip(self):
        """Test phone format stripping."""
        self.assertEqual(strip_format("(123) 456-7890", "phone"), "1234567890")

    def test_ein_format_apply(self):
        """Test EIN formatting."""
        self.assertEqual(apply_format("123456789", "ein"), "12-3456789")

    def test_credit_card_format_apply(self):
        """Test credit card formatting."""
        self.assertEqual(
            apply_format("1234567890123456", "credit_card"), "1234-5678-9012-3456"
        )

    def test_format_none_value(self):
        """Test formatting None returns None."""
        self.assertIsNone(apply_format(None, "ssn"))
        self.assertIsNone(strip_format(None, "ssn"))

    def test_format_unknown_pattern(self):
        """Test unknown format pattern returns value unchanged."""
        self.assertEqual(apply_format("12345", "unknown"), "12345")
        self.assertEqual(strip_format("12345", "unknown"), "12345")


@tagged("post_install", "-at_install")
class TestEncryptedFieldMasking(TransactionCase):
    """Test masking functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_mask_full(self):
        """Test full masking."""
        field = Encrypted(mask="full")
        self.assertEqual(field._mask_value("123456789"), "*********")

    def test_mask_last4(self):
        """Test last4 masking."""
        field = Encrypted(mask="last4")
        self.assertEqual(field._mask_value("123456789"), "*****6789")

    def test_mask_first4(self):
        """Test first4 masking."""
        field = Encrypted(mask="first4")
        self.assertEqual(field._mask_value("123456789"), "1234*****")

    def test_mask_preserves_format_chars(self):
        """Test that masking preserves format characters."""
        field = Encrypted(mask="last4", format="ssn")
        # With SSN format, 123456789 becomes 123-45-6789
        # Last 4 alphanumeric should show: ***-**-6789
        masked = field._mask_value("123456789")
        self.assertIn("-", masked)
        self.assertTrue(masked.endswith("6789"))

    def test_mask_short_value_last4(self):
        """Test masking value shorter than 4 chars."""
        field = Encrypted(mask="last4")
        self.assertEqual(field._mask_value("123"), "123")

    def test_mask_callable(self):
        """Test custom callable masking."""

        def custom_mask(value):
            return f"[REDACTED:{len(value)}]"

        field = Encrypted(mask=custom_mask)
        self.assertEqual(field._mask_value("secret"), "[REDACTED:6]")

    def test_mask_none_value(self):
        """Test masking None returns None."""
        field = Encrypted(mask="full")
        self.assertIsNone(field._mask_value(None))


@tagged("post_install", "-at_install")
class TestEncryptedFieldOnModel(TransactionCase):
    """Test Encrypted field behavior on actual Odoo models."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_field_defaults(self):
        """Test that Encrypted field has correct defaults."""
        field = Encrypted(string="Test")
        self.assertEqual(field.mask, "full")
        self.assertTrue(field.audit)
        self.assertIsNone(field.encrypt_groups)
        self.assertIsNone(field.format)

    def test_field_copy_default_false(self):
        """Test that copy defaults to False via kwargs."""
        field = Encrypted(string="Test")
        # Check args dict which stores the kwargs passed to parent
        self.assertIn("copy", field.args)
        self.assertFalse(field.args["copy"])

    def test_field_tracking_default_false(self):
        """Test that tracking defaults to False via kwargs."""
        field = Encrypted(string="Test")
        # Check args dict which stores the kwargs passed to parent
        self.assertIn("tracking", field.args)
        self.assertFalse(field.args["tracking"])

    def test_field_column_type_is_text(self):
        """Test that column type is TEXT for encrypted data."""
        field = Encrypted(string="Test")
        self.assertEqual(field.column_type, ("text", "TEXT"))


@tagged("post_install", "-at_install")
class TestEncryptedFieldAccessControl(TransactionCase):
    """Test group-based access control."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

        cls.admin_user = cls.env.ref("base.user_admin")
        # Create a test user without system group for access control tests
        cls.basic_user = cls.env["res.users"].create(
            {
                "name": "Test Basic User",
                "login": "test_basic_user_encrypted",
                "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
            }
        )

    def test_user_has_access_no_groups(self):
        """Test that no groups means everyone has access."""
        field = Encrypted(encrypt_groups=None)
        env_admin = self.env(user=self.admin_user)
        self.assertTrue(field._user_has_access(env_admin))

    def test_user_has_access_with_group(self):
        """Test access with specific group requirement."""
        field = Encrypted(encrypt_groups="base.group_system")
        env_admin = self.env(user=self.admin_user)
        self.assertTrue(field._user_has_access(env_admin))

    def test_user_no_access_without_group(self):
        """Test no access when user lacks required group."""
        field = Encrypted(encrypt_groups="base.group_system")
        env_basic = self.env(user=self.basic_user)
        # Basic user doesn't have system group
        self.assertFalse(field._user_has_access(env_basic))

    def test_user_access_multiple_groups(self):
        """Test access with comma-separated groups."""
        field = Encrypted(encrypt_groups="base.group_user, base.group_system")
        env_basic = self.env(user=self.basic_user)
        # Basic user has base.group_user
        self.assertTrue(field._user_has_access(env_basic))
