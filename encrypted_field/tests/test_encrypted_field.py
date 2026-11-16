from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged
from odoo.tools import config

from ..fields.encrypted import (
    Encrypted,
    apply_format,
    decrypt_value,
    encrypt_value,
    is_encrypted_value,
    strip_format,
)


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
        field = Encrypted(mask="last4", format_pattern="ssn")
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
        self.assertIsNone(field.format_pattern)

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


@tagged("post_install", "-at_install")
class TestEncryptedFieldConversions(TransactionCase):
    """Test field conversion methods."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_convert_to_column_with_value(self):
        """Test converting value to database column format."""
        field = Encrypted(string="Test")
        # Mock record with minimal interface
        encrypted = field.convert_to_column("secret123", None, None, True)
        self.assertTrue(is_encrypted_value(encrypted))
        # Verify can decrypt back
        self.assertEqual(decrypt_value(encrypted), "secret123")

    def test_convert_to_column_none(self):
        """Test converting None returns None."""
        field = Encrypted(string="Test")
        self.assertIsNone(field.convert_to_column(None, None, None, True))

    def test_convert_to_column_false(self):
        """Test converting False returns None."""
        field = Encrypted(string="Test")
        self.assertIsNone(field.convert_to_column(False, None, None, True))

    def test_convert_to_column_integer(self):
        """Test converting integer to string then encrypting."""
        field = Encrypted(string="Test")
        encrypted = field.convert_to_column(12345, None, None, True)
        self.assertTrue(is_encrypted_value(encrypted))
        self.assertEqual(decrypt_value(encrypted), "12345")

    def test_convert_to_column_strips_format(self):
        """Test that formatting is stripped before encryption."""
        field = Encrypted(string="Test", format_pattern="ssn")
        encrypted = field.convert_to_column("123-45-6789", None, None, True)
        # Should store as 123456789 (stripped)
        decrypted = decrypt_value(encrypted)
        self.assertEqual(decrypted, "123456789")

    def test_convert_to_cache_encrypted_value(self):
        """Test converting encrypted value from database to cache."""
        field = Encrypted(string="Test")
        encrypted = encrypt_value("myvalue")
        decrypted = field.convert_to_cache(encrypted, None, True)
        self.assertEqual(decrypted, "myvalue")

    def test_convert_to_cache_none(self):
        """Test converting None returns None."""
        field = Encrypted(string="Test")
        self.assertIsNone(field.convert_to_cache(None, None, True))

    def test_convert_to_cache_false(self):
        """Test converting False returns None."""
        field = Encrypted(string="Test")
        self.assertIsNone(field.convert_to_cache(False, None, True))

    def test_convert_to_cache_plain_value(self):
        """Test that non-encrypted values pass through."""
        field = Encrypted(string="Test")
        # Short value that doesn't look encrypted
        result = field.convert_to_cache("plain", None, True)
        self.assertEqual(result, "plain")

    def test_convert_to_cache_non_string(self):
        """Test that non-string values pass through."""
        field = Encrypted(string="Test")
        result = field.convert_to_cache(12345, None, True)
        self.assertEqual(result, 12345)

    def test_convert_to_record_masks_value(self):
        """Test that convert_to_record returns masked value."""
        field = Encrypted(string="Test", mask="last4")
        result = field.convert_to_record("123456789", None)
        self.assertEqual(result, "*****6789")

    def test_convert_to_record_none(self):
        """Test converting None returns None."""
        field = Encrypted(string="Test")
        self.assertIsNone(field.convert_to_record(None, None))

    def test_convert_to_record_decrypts_then_masks(self):
        """Test that encrypted values are decrypted then masked."""
        field = Encrypted(string="Test", mask="last4")
        encrypted = encrypt_value("123456789")
        result = field.convert_to_record(encrypted, None)
        self.assertEqual(result, "*****6789")

    def test_convert_to_read(self):
        """Test convert_to_read delegates to convert_to_record."""
        field = Encrypted(string="Test", mask="full")
        result = field.convert_to_read("secret", None, True)
        self.assertEqual(result, "******")

    def test_convert_to_write_value(self):
        """Test convert_to_write passes value through."""
        field = Encrypted(string="Test")
        result = field.convert_to_write("myvalue", None)
        self.assertEqual(result, "myvalue")

    def test_convert_to_write_none(self):
        """Test convert_to_write with None."""
        field = Encrypted(string="Test")
        self.assertIsNone(field.convert_to_write(None, None))

    def test_convert_to_write_false(self):
        """Test convert_to_write with False."""
        field = Encrypted(string="Test")
        self.assertIsNone(field.convert_to_write(False, None))

    def test_convert_to_export_masks_value(self):
        """Test that export returns masked value."""
        field = Encrypted(string="Test", mask="last4", audit=False)
        result = field.convert_to_export("123456789", None)
        self.assertEqual(result, "*****6789")

    def test_convert_to_export_none(self):
        """Test export with None returns empty string."""
        field = Encrypted(string="Test")
        self.assertEqual(field.convert_to_export(None, None), "")

    def test_convert_to_display_name(self):
        """Test convert_to_display_name masks value."""
        field = Encrypted(string="Test", mask="full")
        result = field.convert_to_display_name("secret", None)
        self.assertEqual(result, "******")


@tagged("post_install", "-at_install")
class TestEncryptedFieldSearchBlock(TransactionCase):
    """Test that search operations are blocked."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_determine_domain_raises_error(self):
        """Test that search on encrypted field raises error."""
        field = Encrypted(string="Test")
        field.name = "test_field"  # Set name for error message
        with self.assertRaises(UserError) as cm:
            field.determine_domain(None, "=", "value")
        self.assertIn("Search operations are not allowed", str(cm.exception))
        self.assertIn("test_field", str(cm.exception))


@tagged("post_install", "-at_install")
class TestEncryptedFieldMaskingEdgeCases(TransactionCase):
    """Test masking edge cases."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_mask_empty_string(self):
        """Test masking empty string returns empty."""
        field = Encrypted(mask="full")
        self.assertEqual(field._mask_value(""), "")

    def test_mask_short_value_first4(self):
        """Test masking value shorter than 4 chars with first4."""
        field = Encrypted(mask="first4")
        self.assertEqual(field._mask_value("12"), "12")

    def test_mask_exactly_4_chars_last4(self):
        """Test masking exactly 4 char value with last4."""
        field = Encrypted(mask="last4")
        self.assertEqual(field._mask_value("1234"), "1234")

    def test_mask_exactly_4_chars_first4(self):
        """Test masking exactly 4 char value with first4."""
        field = Encrypted(mask="first4")
        self.assertEqual(field._mask_value("1234"), "1234")

    def test_mask_with_special_chars(self):
        """Test masking preserves non-alphanumeric chars."""
        field = Encrypted(mask="full")
        result = field._mask_value("123-456")
        self.assertEqual(result, "***-***")

    def test_mask_last4_with_format(self):
        """Test last4 mask with format pattern applied."""
        field = Encrypted(mask="last4", format_pattern="phone")
        # Input: 1234567890 -> formatted: (123) 456-7890
        # Last 4 alphanumeric shown: (***) ***-7890
        result = field._mask_value("1234567890")
        self.assertIn("7890", result)
        self.assertIn(")", result)  # Format chars preserved


@tagged("post_install", "-at_install")
class TestFormatPatternsEdgeCases(TransactionCase):
    """Test format pattern edge cases."""

    def test_strip_format_no_pattern(self):
        """Test strip with no format_name."""
        self.assertEqual(strip_format("123-45-6789", None), "123-45-6789")
        self.assertEqual(strip_format("123-45-6789", ""), "123-45-6789")

    def test_apply_format_no_pattern(self):
        """Test apply with no format_name."""
        self.assertEqual(apply_format("123456789", None), "123456789")
        self.assertEqual(apply_format("123456789", ""), "123456789")

    def test_apply_format_value_longer_than_pattern(self):
        """Test formatting when value is longer than pattern."""
        # EIN pattern is ##-####### (9 digits)
        # Value with 12 digits
        result = apply_format("123456789012", "ein")
        # Should apply pattern and append remainder
        self.assertTrue(result.startswith("12-3456789"))

    def test_apply_format_value_shorter_than_pattern(self):
        """Test formatting when value is shorter than pattern."""
        # SSN pattern is ###-##-#### (9 digits)
        # Value with 5 digits
        result = apply_format("12345", "ssn")
        self.assertEqual(result, "123-45")

    def test_credit_card_strip(self):
        """Test credit card format stripping."""
        result = strip_format("1234-5678-9012-3456", "credit_card")
        self.assertEqual(result, "1234567890123456")

    def test_ein_strip(self):
        """Test EIN format stripping."""
        result = strip_format("12-3456789", "ein")
        self.assertEqual(result, "123456789")


@tagged("post_install", "-at_install")
class TestEncryptedFieldLogging(TransactionCase):
    """Test audit logging functionality on encrypted fields."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

        cls.admin_user = cls.env.ref("base.user_admin")

    def test_log_access_creates_audit_entry(self):
        """Test that _log_access creates audit log entry."""
        field = Encrypted(string="Test", audit=True)
        field._log_access(self.env, 1, "test_field", "res.partner", "decrypt")

        # Verify log was created
        log = self.env["pb.encrypted.audit.log"].search(
            [
                ("model_name", "=", "res.partner"),
                ("field_name", "=", "test_field"),
                ("record_id", "=", 1),
            ],
            limit=1,
        )
        self.assertTrue(log)

    def test_log_access_disabled(self):
        """Test that _log_access does nothing when audit=False."""
        field = Encrypted(string="Test", audit=False)
        # Should not raise and should not create log
        field._log_access(self.env, 999, "no_audit_field", "test.model", "decrypt")

        log = self.env["pb.encrypted.audit.log"].search(
            [
                ("field_name", "=", "no_audit_field"),
                ("record_id", "=", 999),
            ],
            limit=1,
        )
        self.assertFalse(log)


@tagged("post_install", "-at_install")
class TestEncryptedFieldFormatting(TransactionCase):
    """Test field formatting methods."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_format_value_with_pattern(self):
        """Test _format_value with SSN pattern."""
        field = Encrypted(string="Test", format_pattern="ssn")
        result = field._format_value("123456789")
        self.assertEqual(result, "123-45-6789")

    def test_format_value_no_pattern(self):
        """Test _format_value without pattern."""
        field = Encrypted(string="Test")
        result = field._format_value("123456789")
        self.assertEqual(result, "123456789")

    def test_format_value_none(self):
        """Test _format_value with None."""
        field = Encrypted(string="Test", format_pattern="ssn")
        result = field._format_value(None)
        self.assertIsNone(result)

    def test_strip_format_with_pattern(self):
        """Test _strip_format with SSN pattern."""
        field = Encrypted(string="Test", format_pattern="ssn")
        result = field._strip_format("123-45-6789")
        self.assertEqual(result, "123456789")

    def test_strip_format_no_pattern(self):
        """Test _strip_format without pattern."""
        field = Encrypted(string="Test")
        result = field._strip_format("123-45-6789")
        self.assertEqual(result, "123-45-6789")

    def test_strip_format_none(self):
        """Test _strip_format with None."""
        field = Encrypted(string="Test", format_pattern="ssn")
        result = field._strip_format(None)
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestEncryptionKeyHandling(TransactionCase):
    """Test encryption key handling and error cases."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_decrypt_invalid_encrypted_value(self):
        """Test decrypting corrupted encrypted value."""
        # Create a value that looks encrypted but is invalid
        invalid_encrypted = "gA" + "x" * 100
        with self.assertRaises(UserError):
            decrypt_value(invalid_encrypted)

    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        result = encrypt_value("")
        # Empty string should still be encrypted
        self.assertTrue(is_encrypted_value(result))
        self.assertEqual(decrypt_value(result), "")

    def test_is_encrypted_short_ga_string(self):
        """Test that short 'gA' strings are not considered encrypted."""
        # Less than 50 chars should not be considered encrypted
        self.assertFalse(is_encrypted_value("gA12345"))
        self.assertFalse(is_encrypted_value("gA"))


@tagged("post_install", "-at_install")
class TestEncryptedFieldCustomInit(TransactionCase):
    """Test Encrypted field initialization options."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_field_with_all_options(self):
        """Test creating field with all custom options."""
        field = Encrypted(
            string="Custom Field",
            encrypt_groups="base.group_system",
            mask="last4",
            audit=False,
            format_pattern="phone",
        )
        self.assertEqual(field.encrypt_groups, "base.group_system")
        self.assertEqual(field.mask, "last4")
        self.assertFalse(field.audit)
        self.assertEqual(field.format_pattern, "phone")

    def test_field_override_copy_tracking(self):
        """Test that copy and tracking can be overridden."""
        field = Encrypted(string="Test", copy=True, tracking=True)
        self.assertTrue(field.args.get("copy"))
        self.assertTrue(field.args.get("tracking"))


@tagged("post_install", "-at_install")
class TestConvertToCacheDecryptError(TransactionCase):
    """Test convert_to_cache decrypt error handling."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_convert_to_cache_invalid_encrypted_returns_none(self):
        """Test that convert_to_cache returns None for invalid encrypted data."""
        field = Encrypted(string="Test")
        # Create invalid encrypted value (looks encrypted but isn't valid)
        invalid = "gA" + "B" * 100  # Looks like Fernet but invalid
        result = field.convert_to_cache(invalid, None, True)
        # Should return None on decrypt error
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestConvertToRecordDecryptError(TransactionCase):
    """Test convert_to_record decrypt error handling."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_convert_to_record_invalid_encrypted_returns_none(self):
        """Test that convert_to_record returns None for invalid encrypted."""
        field = Encrypted(string="Test")
        invalid = "gA" + "C" * 100
        result = field.convert_to_record(invalid, None)
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestConvertToExportDecryptError(TransactionCase):
    """Test convert_to_export decrypt error handling."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_convert_to_export_invalid_encrypted_returns_empty(self):
        """Test that convert_to_export returns empty for invalid encrypted."""
        field = Encrypted(string="Test", audit=False)
        invalid = "gA" + "D" * 100
        result = field.convert_to_export(invalid, None)
        self.assertEqual(result, "")

    def test_convert_to_export_decrypts_valid(self):
        """Test export with valid encrypted value."""
        field = Encrypted(string="Test", mask="last4", audit=False)
        encrypted = encrypt_value("123456789")
        result = field.convert_to_export(encrypted, None)
        # Should return masked value
        self.assertEqual(result, "*****6789")
