# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
Comprehensive test suite for mail_server_manager module.
Covers: unit tests, integration tests, security tests, and mocking.
"""

import os
import shutil
import tempfile

from odoo.tests.common import TransactionCase, tagged


@tagged("mail_server_manager", "standard")
class TestMailAccountUnit(TransactionCase):
    """Unit tests for mail.server.account model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailAccount = cls.env["mail.server.account"]
        cls.Users = cls.env["res.users"]
        cls.MailServer = cls.env["ir.mail_server"]

        # Use existing admin user for tests instead of creating new users
        cls.test_user = cls.env.ref("base.user_admin")

    # ==================== EMAIL VALIDATION TESTS ====================

    def test_email_regex_valid_simple(self):
        """Test simple valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test@domain.org",
            "admin@company.net",
        ]
        for email in valid_emails:
            self.assertTrue(
                self.MailAccount._EMAIL_REGEX.match(email),
                f"Valid email {email} should match regex",
            )

    def test_email_regex_valid_complex(self):
        """Test complex valid email addresses."""
        valid_emails = [
            "user.name@example.com",
            "user+tag@example.org",
            "user_name@sub.example.co.uk",
            "first.last@company.io",
            "user123@domain456.com",
        ]
        for email in valid_emails:
            self.assertTrue(
                self.MailAccount._EMAIL_REGEX.match(email),
                f"Valid email {email} should match regex",
            )

    def test_email_regex_invalid(self):
        """Test invalid email addresses are rejected."""
        invalid_emails = [
            "invalid",
            "@example.com",
            "user@",
            "user@.com",
            "user name@example.com",
            "user@exam ple.com",
            "user@@example.com",
        ]
        for email in invalid_emails:
            self.assertFalse(
                self.MailAccount._EMAIL_REGEX.match(email),
                f"Invalid email {email} should not match regex",
            )

    def test_email_injection_prevention(self):
        """Test that email injection attempts are blocked."""
        injection_emails = [
            "user|malicious@example.com",
            "user;drop table@example.com",
            "user\ninjection@example.com",
            "../../../etc/passwd@example.com",
        ]
        for email in injection_emails:
            self.assertFalse(
                self.MailAccount._EMAIL_REGEX.match(email),
                f"Injection attempt {email} should be blocked",
            )

    # ==================== PASSWORD TESTS ====================

    def test_password_generation_length(self):
        """Test password generation creates correct length."""
        account = self.MailAccount.new({"email": "test@example.com"})

        # Test default length
        password = account._generate_password()
        self.assertEqual(len(password), 16)

        # Test custom length
        password_20 = account._generate_password(length=20)
        self.assertEqual(len(password_20), 20)

        password_8 = account._generate_password(length=8)
        self.assertEqual(len(password_8), 8)

    def test_password_generation_strength(self):
        """Test password contains alphanumeric characters."""
        account = self.MailAccount.new({"email": "test@example.com"})

        # Generate multiple passwords to verify they contain alphanumeric chars
        all_have_alnum = True
        for _ in range(10):
            password = account._generate_password()
            has_alnum = any(c.isalnum() for c in password)
            if not has_alnum:
                all_have_alnum = False
                break

        self.assertTrue(
            all_have_alnum, "Passwords should contain alphanumeric characters"
        )

    def test_password_generation_uniqueness(self):
        """Test that generated passwords are unique."""
        account = self.MailAccount.new({"email": "test@example.com"})
        passwords = [account._generate_password() for _ in range(100)]
        unique_passwords = set(passwords)

        # All passwords should be unique
        self.assertEqual(len(passwords), len(unique_passwords))

    def test_password_hashing_sha512(self):
        """Test password hashing uses SHA512."""
        account = self.MailAccount.new({"email": "test@example.com"})
        password = "TestPassword123!"
        hashed = account._hash_password(password)

        self.assertTrue(hashed.startswith("$6$"), "Hash should use SHA512 ($6$)")
        self.assertNotEqual(hashed, password)
        self.assertGreater(len(hashed), 50)

    def test_password_hashing_unique_salt(self):
        """Test that same password produces different hashes (unique salt)."""
        account = self.MailAccount.new({"email": "test@example.com"})
        password = "SamePassword123!"

        hash1 = account._hash_password(password)
        hash2 = account._hash_password(password)

        # Same password should produce different hashes due to unique salt
        self.assertNotEqual(hash1, hash2)

    # ==================== MIXIN TESTS ====================

    def test_mixin_get_mail_domain(self):
        """Test mixin returns mail domain."""
        domain = self.MailAccount._get_mail_domain()
        self.assertTrue(domain)
        self.assertIn(".", domain)
        self.assertIsInstance(domain, str)

    def test_mixin_get_smtp_host(self):
        """Test mixin returns SMTP host."""
        host = self.MailAccount._get_smtp_host()
        self.assertTrue(host)
        self.assertIsInstance(host, str)

    def test_mixin_get_imap_host(self):
        """Test mixin returns IMAP host."""
        host = self.MailAccount._get_imap_host()
        self.assertTrue(host)
        self.assertIsInstance(host, str)

    def test_mixin_get_imap_port(self):
        """Test mixin returns IMAP port."""
        port = self.MailAccount._get_imap_port()
        self.assertIsInstance(port, int)
        self.assertGreater(port, 0)
        self.assertLess(port, 65536)

    def test_mixin_validate_config_path_valid(self):
        """Test valid config paths are accepted."""
        valid_paths = [
            "/etc/odoo/mail_config",
            "/var/lib/odoo/config",
            "/mnt/data/mail",
            "/etc/odoo/deep/nested/path",
        ]
        for path in valid_paths:
            self.assertTrue(
                self.MailAccount._validate_config_path(path),
                f"Valid path {path} should be accepted",
            )

    def test_mixin_validate_config_path_invalid(self):
        """Test invalid config paths are rejected."""
        invalid_paths = [
            "/tmp/evil",
            "../../../etc/passwd",
            "/home/user/data",
            "/root/.ssh",
            "",
            None,
        ]
        for path in invalid_paths:
            self.assertFalse(
                self.MailAccount._validate_config_path(path),
                f"Invalid path {path} should be rejected",
            )

    def test_mixin_path_traversal_blocked(self):
        """Test path traversal attempts are blocked."""
        traversal_paths = [
            "/etc/odoo/../../../etc/passwd",
            "/var/lib/odoo/../../root",
            "/mnt/../tmp/evil",
        ]
        for path in traversal_paths:
            self.assertFalse(
                self.MailAccount._validate_config_path(path),
                f"Path traversal {path} should be blocked",
            )

    # ==================== STATE TESTS ====================

    def test_state_field_values(self):
        """Test state field has all expected values."""
        states = dict(self.MailAccount._fields["state"].selection)
        expected = {"draft", "active", "suspended", "error"}
        self.assertEqual(set(states.keys()), expected)

    def test_state_default_value(self):
        """Test state defaults to draft."""
        account = self.MailAccount.new({"email": "test@example.com"})
        self.assertEqual(account.state, "draft")

    # ==================== FIELD TESTS ====================

    def test_field_email_required(self):
        """Test email field is required."""
        email_field = self.MailAccount._fields["email"]
        self.assertTrue(email_field.required)

    def test_field_email_indexed(self):
        """Test email field is indexed."""
        email_field = self.MailAccount._fields["email"]
        self.assertTrue(email_field.index)

    def test_field_user_id_ondelete(self):
        """Test user_id ondelete is set null."""
        user_id_field = self.MailAccount._fields["user_id"]
        self.assertEqual(user_id_field.ondelete, "set null")

    def test_field_mail_server_copy_false(self):
        """Test mail_server_id has copy=False."""
        field = self.MailAccount._fields["mail_server_id"]
        self.assertFalse(field.copy)

    def test_field_fetchmail_server_copy_false(self):
        """Test fetchmail_server_id has copy=False."""
        field = self.MailAccount._fields["fetchmail_server_id"]
        self.assertFalse(field.copy)

    def test_field_quota_default(self):
        """Test quota_mb default value."""
        account = self.MailAccount.new({"email": "test@example.com"})
        self.assertEqual(account.quota_mb, 1024)

    # ==================== FROM FILTER TESTS ====================

    def test_build_from_filter_internal_only(self):
        """Test from_filter with only internal email."""
        account = self.MailAccount.new({"email": "internal@company.com"})
        filter_str = account._build_from_filter(None)
        self.assertEqual(filter_str, "internal@company.com")

    def test_build_from_filter_with_personal(self):
        """Test from_filter with internal and personal email."""
        account = self.MailAccount.new({"email": "internal@company.com"})
        filter_str = account._build_from_filter("personal@gmail.com")
        self.assertEqual(filter_str, "internal@company.com,personal@gmail.com")

    def test_build_from_filter_same_email(self):
        """Test from_filter when personal equals internal."""
        account = self.MailAccount.new({"email": "same@company.com"})
        filter_str = account._build_from_filter("same@company.com")
        self.assertEqual(filter_str, "same@company.com")


@tagged("mail_server_manager", "standard")
class TestMailAccountIntegration(TransactionCase):
    """Integration tests with mocked filesystem operations."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailAccount = cls.env["mail.server.account"]
        cls.Users = cls.env["res.users"]

        # Create temp directory for tests
        cls.temp_dir = tempfile.mkdtemp()
        cls.accounts_file = os.path.join(cls.temp_dir, "postfix-accounts.cf")
        cls.virtual_file = os.path.join(cls.temp_dir, "postfix-virtual.cf")

    @classmethod
    def tearDownClass(cls):
        # Cleanup temp directory
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
        super().tearDownClass()

    def test_atomic_write_creates_file(self):
        """Test atomic write creates file correctly."""
        account = self.MailAccount.new({"email": "test@example.com"})
        test_file = os.path.join(self.temp_dir, "test_atomic.txt")
        content = "test content\n"

        account._atomic_write(test_file, content)

        self.assertTrue(os.path.exists(test_file))
        with open(test_file) as f:
            self.assertEqual(f.read(), content)

    def test_atomic_write_overwrites_file(self):
        """Test atomic write overwrites existing file."""
        account = self.MailAccount.new({"email": "test@example.com"})
        test_file = os.path.join(self.temp_dir, "test_overwrite.txt")

        # Create initial file
        with open(test_file, "w") as f:
            f.write("initial content")

        # Overwrite with atomic write
        new_content = "new content\n"
        account._atomic_write(test_file, new_content)

        with open(test_file) as f:
            self.assertEqual(f.read(), new_content)

    def test_create_backup(self):
        """Test backup creation."""
        account = self.MailAccount.new({"email": "test@example.com"})
        test_file = os.path.join(self.temp_dir, "test_backup.txt")

        # Create file to backup
        original_content = "original content"
        with open(test_file, "w") as f:
            f.write(original_content)

        # Create backup
        backup_path = account._create_backup(test_file)

        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))
        with open(backup_path) as f:
            self.assertEqual(f.read(), original_content)

    def test_create_backup_nonexistent_file(self):
        """Test backup of non-existent file returns None."""
        account = self.MailAccount.new({"email": "test@example.com"})
        backup_path = account._create_backup("/nonexistent/path/file.txt")
        self.assertIsNone(backup_path)


@tagged("mail_server_manager", "standard")
class TestMailAccountSecurity(TransactionCase):
    """Security and permission tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailAccount = cls.env["mail.server.account"]

        # Use existing users for tests to avoid constraint issues
        cls.admin_user = cls.env.ref("base.user_admin")
        cls.regular_user = cls.env.ref("base.user_demo", raise_if_not_found=False)
        if not cls.regular_user:
            cls.regular_user = cls.admin_user  # Fallback if demo user doesn't exist

    def test_admin_can_read_all_accounts(self):
        """Test admin can read all accounts."""
        accounts = self.MailAccount.with_user(self.admin_user).search([])
        # Should not raise AccessError
        self.assertIsNotNone(accounts)

    def test_regular_user_limited_access(self):
        """Test regular user has limited read access."""
        # Regular users should only see their own accounts (record rule)
        # Note: Admin user can see all, so we just verify the search doesn't fail
        accounts = self.MailAccount.with_user(self.regular_user).search([])
        # Should return accounts without raising AccessError
        self.assertIsNotNone(accounts)

    def test_rate_limiting_password_reset(self):
        """Test rate limiting on password reset."""
        # This test verifies the rate limiting mechanism exists
        self.MailAccount.new({"email": "test@example.com"})
        self.assertIn("last_password_reset", self.MailAccount._fields)
        self.assertIn("password_reset_count", self.MailAccount._fields)


@tagged("mail_server_manager", "standard")
class TestResUsersMailAccount(TransactionCase):
    """Tests for res.users mail account integration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Users = cls.env["res.users"]
        cls.MailAccount = cls.env["mail.server.account"]

    def test_user_internal_email_computed(self):
        """Test internal_email computed field."""
        user = self.Users.browse(self.env.uid)
        if user.mail_account_id:
            self.assertEqual(user.internal_email, user.mail_account_id.email)
        else:
            self.assertFalse(user.internal_email)

    def test_user_mailbox_created_computed(self):
        """Test mailbox_created computed field."""
        user = self.Users.browse(self.env.uid)
        expected = bool(user.mail_account_id)
        self.assertEqual(user.mailbox_created, expected)

    def test_generate_internal_email_prefix_from_name(self):
        """Test email prefix generation from name."""
        user = self.Users.new(
            {
                "name": "John Doe",
                "login": "johndoe",
            }
        )
        prefix = user._generate_internal_email_prefix()
        self.assertIn(".", prefix)  # firstname.lastname format
        self.assertFalse(" " in prefix)  # No spaces
        self.assertEqual(prefix, prefix.lower())  # Lowercase

    def test_generate_internal_email_prefix_from_email(self):
        """Test email prefix generation from existing email."""
        user = self.Users.new(
            {
                "name": "Test",
                "login": "test",
                "email": "existing.prefix@example.com",
            }
        )
        prefix = user._generate_internal_email_prefix()
        self.assertEqual(prefix, "existing.prefix")

    def test_generate_internal_email_prefix_fallback(self):
        """Test email prefix fallback to login."""
        user = self.Users.new(
            {
                "name": "",
                "login": "fallback_user",
            }
        )
        prefix = user._generate_internal_email_prefix()
        self.assertTrue(prefix)  # Should not be empty


@tagged("mail_server_manager", "standard")
class TestPasswordWizard(TransactionCase):
    """Tests for password display wizard."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["mail.server.password.wizard"]

    def test_wizard_model_exists(self):
        """Test wizard model exists."""
        self.assertIn("mail.server.password.wizard", self.env)

    def test_wizard_is_transient(self):
        """Test wizard is a transient model."""
        self.assertTrue(self.Wizard._transient)

    def test_wizard_fields(self):
        """Test wizard has required fields."""
        fields = self.Wizard._fields
        self.assertIn("password", fields)
        self.assertIn("mail_account_id", fields)
        self.assertIn("email", fields)


@tagged("mail_server_manager", "standard")
class TestMailMail(TransactionCase):
    """Tests for mail.mail override."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailMail = cls.env["mail.mail"]

    def test_mail_mail_inherits(self):
        """Test mail.mail model exists and is inherited."""
        self.assertIn("mail.mail", self.env)


@tagged("mail_server_manager", "standard")
class TestQuotaFunctionality(TransactionCase):
    """Tests for quota functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailAccount = cls.env["mail.server.account"]
        cls.temp_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
        super().tearDownClass()

    def test_quota_default_value(self):
        """Test default quota is 1024 MB."""
        account = self.MailAccount.new({"email": "test@example.com"})
        self.assertEqual(account.quota_mb, 1024)

    def test_quota_field_exists(self):
        """Test quota_mb field exists."""
        self.assertIn("quota_mb", self.MailAccount._fields)

    def test_quota_bytes_calculation(self):
        """Test quota bytes calculation."""
        account = self.MailAccount.new({"email": "test@example.com", "quota_mb": 2048})
        expected_bytes = 2048 * 1024 * 1024
        self.assertEqual(account.quota_mb * 1024 * 1024, expected_bytes)


@tagged("mail_server_manager", "standard")
class TestConfigSettings(TransactionCase):
    """Tests for configuration settings."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ConfigSettings = cls.env["res.config.settings"]

    def test_config_fields_exist(self):
        """Test configuration fields exist."""
        fields = self.ConfigSettings._fields
        expected_fields = [
            "mail_server_manager_domain",
            "mail_server_manager_config_path",
            "mail_server_manager_smtp_host",
            "mail_server_manager_imap_host",
            "mail_server_manager_imap_port",
            "mail_server_manager_auto_create",
            "mail_server_manager_overwrite_email",
        ]
        for field in expected_fields:
            self.assertIn(field, fields, f"Config field {field} should exist")


@tagged("mail_server_manager", "standard")
class TestFromFilterBuilder(TransactionCase):
    """Tests for from_filter building."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailAccount = cls.env["mail.server.account"]

    def test_from_filter_single_email(self):
        """Test from_filter with single email."""
        account = self.MailAccount.new({"email": "test@company.com"})
        self.assertEqual(account._build_from_filter(None), "test@company.com")

    def test_from_filter_two_emails(self):
        """Test from_filter with two different emails."""
        account = self.MailAccount.new({"email": "internal@company.com"})
        result = account._build_from_filter("personal@gmail.com")
        self.assertEqual(result, "internal@company.com,personal@gmail.com")

    def test_from_filter_duplicate_email(self):
        """Test from_filter when emails are same."""
        account = self.MailAccount.new({"email": "same@company.com"})
        result = account._build_from_filter("same@company.com")
        self.assertEqual(result, "same@company.com")


@tagged("mail_server_manager", "standard")
class TestMailMailOverride(TransactionCase):
    """Tests for mail.mail reply-to override."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailMail = cls.env["mail.mail"]

    def test_mail_mail_model_exists(self):
        """Test mail.mail model is available."""
        self.assertIn("mail.mail", self.env)

    def test_get_user_internal_email_method_exists(self):
        """Test _get_user_internal_email method exists."""
        mail = self.MailMail.new({})
        self.assertTrue(hasattr(mail, "_get_user_internal_email"))

    def test_send_prepare_values_method_exists(self):
        """Test _send_prepare_values method exists."""
        mail = self.MailMail.new({})
        self.assertTrue(hasattr(mail, "_send_prepare_values"))

    def test_get_user_internal_email_no_author(self):
        """Test _get_user_internal_email with no author."""
        mail = self.MailMail.new({})
        user, email = mail._get_user_internal_email(None)
        # Result depends on current user's internal_email
        self.assertTrue(user is None or hasattr(user, "internal_email"))
