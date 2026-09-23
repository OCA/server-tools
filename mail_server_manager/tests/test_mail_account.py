# Part of Odoo. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMailServerAccount(TransactionCase):
    """Unit tests for mail.server.account model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailAccount = cls.env["mail.server.account"]
        cls.Users = cls.env["res.users"]

    def test_email_validation_valid(self):
        """Test that valid email addresses are accepted."""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.org",
            "user_name@sub.example.co.uk",
        ]
        for email in valid_emails:
            # Should not raise
            self.assertTrue(
                self.MailAccount._EMAIL_REGEX.match(email),
                f"Valid email {email} should match regex",
            )

    def test_email_validation_invalid(self):
        """Test that invalid email addresses are rejected."""
        invalid_emails = [
            "invalid",
            "@example.com",
            "user@",
            "user@.com",
            "user@example",
            "user name@example.com",
            "user@exam ple.com",
        ]
        for email in invalid_emails:
            self.assertFalse(
                self.MailAccount._EMAIL_REGEX.match(email),
                f"Invalid email {email} should not match regex",
            )

    def test_mixin_get_mail_domain(self):
        """Test that mixin returns mail domain from config."""
        domain = self.MailAccount._get_mail_domain()
        self.assertTrue(domain, "Mail domain should be configured")
        self.assertIn(".", domain, "Domain should contain a dot")

    def test_mixin_validate_config_path_valid(self):
        """Test valid config paths are accepted."""
        valid_paths = [
            "/etc/odoo/mail_config",
            "/var/lib/odoo/config",
            "/mnt/data/mail",
        ]
        for path in valid_paths:
            self.assertTrue(
                self.MailAccount._validate_config_path(path),
                f"Valid path {path} should be accepted",
            )

    def test_mixin_validate_config_path_invalid(self):
        """Test invalid/dangerous config paths are rejected."""
        invalid_paths = [
            "/tmp/evil",
            "../../../etc/passwd",
            "/home/user/data",
            "",
            None,
        ]
        for path in invalid_paths:
            self.assertFalse(
                self.MailAccount._validate_config_path(path),
                f"Invalid path {path} should be rejected",
            )

    def test_password_generation(self):
        """Test password generation creates strong passwords."""
        account = self.MailAccount.new({"email": "test@example.com"})
        password = account._generate_password()

        self.assertEqual(len(password), 16, "Password should be 16 chars")
        self.assertTrue(
            any(c.isdigit() for c in password), "Password should contain digits"
        )
        self.assertTrue(
            any(c.isalpha() for c in password), "Password should contain letters"
        )

    def test_password_hashing(self):
        """Test password hashing uses SHA512."""
        account = self.MailAccount.new({"email": "test@example.com"})
        password = "TestPassword123!"
        hashed = account._hash_password(password)

        self.assertTrue(hashed.startswith("$6$"), "Hash should use SHA512")
        self.assertNotEqual(hashed, password, "Hash should differ from password")

    def test_state_transitions(self):
        """Test that state field has all expected values."""
        states = dict(self.MailAccount._fields["state"].selection)
        expected = {"draft", "active", "suspended", "error"}
        self.assertEqual(set(states.keys()), expected)

    def test_user_internal_email_computed(self):
        """Test that internal_email is computed from mail_account."""
        user = self.Users.browse(self.env.uid)
        if user.mail_account_id:
            self.assertEqual(
                user.internal_email,
                user.mail_account_id.email,
                "Internal email should match mail account email",
            )
        else:
            self.assertFalse(
                user.internal_email,
                "Internal email should be False without mail account",
            )

    def test_constraint_email_unique(self):
        """Test that duplicate email addresses are blocked."""
        email = "unique_test@example.com"
        # Patch file operations to avoid CI environment issues
        with patch.object(
            type(self.MailAccount), "_write_to_accounts_file", return_value=None
        ):
            self.MailAccount.create({"email": email})
            with self.assertRaises(ValidationError):
                self.MailAccount.create({"email": email})
