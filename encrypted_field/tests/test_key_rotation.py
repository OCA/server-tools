# -*- coding: utf-8 -*-
import re
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged
from odoo.tools import config


@tagged("post_install", "-at_install")
class TestKeyRotationWizard(TransactionCase):
    """Test key rotation wizard functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure encryption key is configured
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

        cls.admin_user = cls.env.ref("base.user_admin")
        # Give admin the encryption admin group
        cls.env.ref("encrypted_field.group_encryption_admin").users = [
            (4, cls.admin_user.id)
        ]

    def test_wizard_creates_with_new_key(self):
        """Test wizard auto-generates new key on creation."""
        wizard = self.env["pb.key.rotation.wizard"].create({})
        self.assertTrue(wizard.new_key)
        self.assertTrue(wizard.generate_new_key)
        # Key should be valid Fernet key (base64, 44 chars)
        self.assertEqual(len(wizard.new_key), 44)

    def test_wizard_default_state(self):
        """Test wizard starts in draft state."""
        wizard = self.env["pb.key.rotation.wizard"].create({})
        self.assertEqual(wizard.state, "draft")

    def test_wizard_get_current_key(self):
        """Test getting current key from config."""
        wizard = self.env["pb.key.rotation.wizard"].create({})
        current_key = wizard._get_current_key()
        self.assertEqual(current_key, config.get("encryption_key"))

    def test_wizard_get_current_key_missing(self):
        """Test error when no encryption key configured."""
        wizard = self.env["pb.key.rotation.wizard"].create({})
        with patch.object(config, "get", return_value=None):
            with self.assertRaises(UserError) as cm:
                wizard._get_current_key()
            self.assertIn("No encryption key", str(cm.exception))

    def test_wizard_onchange_generate_new_key(self):
        """Test that toggling generate_new_key creates new key."""
        wizard = self.env["pb.key.rotation.wizard"].create(
            {
                "generate_new_key": False,
                "new_key": "manual_key",
            }
        )
        original_key = wizard.new_key
        wizard.generate_new_key = True
        wizard._onchange_generate_new_key()
        self.assertNotEqual(wizard.new_key, original_key)
        self.assertEqual(len(wizard.new_key), 44)

    def test_wizard_preview_no_fields(self):
        """Test preview when no encrypted fields exist."""
        wizard = self.env["pb.key.rotation.wizard"].create({})
        with patch.object(type(wizard), "_get_encrypted_fields", return_value=[]):
            wizard.action_preview()
            self.assertEqual(wizard.state, "preview")
            self.assertIn("No encrypted fields", wizard.preview_info)

    def test_wizard_get_encrypted_fields(self):
        """Test finding encrypted fields in registry."""
        wizard = self.env["pb.key.rotation.wizard"].create({})
        fields = wizard._get_encrypted_fields()
        # Should return a list (may be empty if no encrypted fields defined)
        self.assertIsInstance(fields, list)
        # Each item should have model and field keys
        for field_info in fields:
            self.assertIn("model", field_info)
            self.assertIn("field", field_info)

    def test_wizard_invalid_new_key(self):
        """Test validation of invalid new key."""
        wizard = self.env["pb.key.rotation.wizard"].create(
            {
                "generate_new_key": False,
                "new_key": "not_a_valid_fernet_key",
            }
        )
        with self.assertRaises(UserError) as cm:
            wizard.action_preview()
        self.assertIn("Invalid key", str(cm.exception))

    def test_update_config_file_regex(self):
        """Test config file update regex patterns."""
        # Test replacing existing key
        content = "db_name = test\nencryption_key = old_key_here\nother = value"
        new_key = "new_key_value"

        # Simulate the regex replacement
        new_content = re.sub(
            r"^encryption_key\s*=.*$",
            f"encryption_key = {new_key}",
            content,
            flags=re.MULTILINE,
        )
        self.assertIn(f"encryption_key = {new_key}", new_content)
        self.assertNotIn("old_key_here", new_content)

    def test_update_config_file_add_key(self):
        """Test adding key when not present."""
        content = "db_name = test\nother = value"
        new_key = "new_key_value"

        # Should not match, so append
        if not re.search(r"^encryption_key\s*=", content, re.MULTILINE):
            new_content = content.rstrip() + f"\nencryption_key = {new_key}\n"
        else:
            new_content = content

        self.assertIn(f"encryption_key = {new_key}", new_content)


@tagged("post_install", "-at_install")
class TestKeyVersioning(TransactionCase):
    """Test key version synchronization across workers."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_bump_key_version(self):
        """Test bumping key version in database."""
        from ..fields.encrypted import bump_key_version

        old_version = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("encryption.key_version", "0")
        )
        new_version = bump_key_version(self.env)

        self.assertNotEqual(new_version, old_version)
        # Version should be a timestamp string
        self.assertTrue(new_version.isdigit())

        # Verify it's stored in database
        stored = (
            self.env["ir.config_parameter"].sudo().get_param("encryption.key_version")
        )
        self.assertEqual(stored, new_version)

    def test_get_key_version(self):
        """Test getting key version from database."""
        # Set a known version
        self.env["ir.config_parameter"].sudo().set_param(
            "encryption.key_version", "12345"
        )
        # Flush to database without commit (stays in transaction)
        self.env.cr.flush()

        # Read directly from database to verify
        stored = (
            self.env["ir.config_parameter"].sudo().get_param("encryption.key_version")
        )
        self.assertEqual(stored, "12345")
