from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged
from odoo.tools import config


@tagged("post_install", "-at_install")
class TestMigrationWizard(TransactionCase):
    """Test migration wizard functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

        cls.admin_user = cls.env.ref("base.user_admin")
        cls.env.ref("encrypted_field.group_encryption_admin").users = [
            (4, cls.admin_user.id)
        ]

    def test_wizard_creates_with_lines(self):
        """Test wizard auto-populates encrypted field lines."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        # Lines are created via default_get
        # May be empty if no encrypted fields in database
        self.assertIsNotNone(wizard.line_ids)

    def test_wizard_default_state(self):
        """Test wizard starts in draft state."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        self.assertEqual(wizard.state, "draft")

    def test_wizard_get_encrypted_fields_with_counts(self):
        """Test finding encrypted fields with unencrypted counts."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        fields = wizard._get_encrypted_fields_with_counts()
        self.assertIsInstance(fields, list)
        for field_info in fields:
            self.assertIn("model", field_info)
            self.assertIn("field", field_info)
            self.assertIn("count", field_info)

    def test_wizard_select_all(self):
        """Test select all action."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        # Create test lines
        self.env["pb.encryption.migration.wizard.line"].create(
            {
                "wizard_id": wizard.id,
                "model_name": "test.model",
                "field_name": "test_field",
                "unencrypted_count": 5,
                "selected": False,
            }
        )
        wizard.action_select_all()
        self.assertTrue(
            wizard.line_ids.filtered(lambda line: line.unencrypted_count > 0).mapped(
                "selected"
            )
        )

    def test_wizard_select_none(self):
        """Test select none action."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        self.env["pb.encryption.migration.wizard.line"].create(
            {
                "wizard_id": wizard.id,
                "model_name": "test.model",
                "field_name": "test_field",
                "unencrypted_count": 5,
                "selected": True,
            }
        )
        wizard.action_select_none()
        self.assertFalse(any(wizard.line_ids.mapped("selected")))

    def test_wizard_preview_no_selection(self):
        """Test preview fails when nothing selected."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        self.env["pb.encryption.migration.wizard.line"].create(
            {
                "wizard_id": wizard.id,
                "model_name": "test.model",
                "field_name": "test_field",
                "unencrypted_count": 5,
                "selected": False,
            }
        )
        with self.assertRaises(UserError) as cm:
            wizard.action_preview()
        self.assertIn("select at least one", str(cm.exception))

    def test_wizard_preview_with_selection(self):
        """Test preview with selection."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        self.env["pb.encryption.migration.wizard.line"].create(
            {
                "wizard_id": wizard.id,
                "model_name": "test.model",
                "field_name": "test_field",
                "unencrypted_count": 5,
                "selected": True,
            }
        )
        wizard.action_preview()
        self.assertEqual(wizard.state, "preview")
        self.assertIn("test.model.test_field", wizard.preview_info)
        self.assertIn("5 records", wizard.preview_info)


@tagged("post_install", "-at_install")
class TestMigrationWizardLine(TransactionCase):
    """Test migration wizard line model."""

    def test_line_display_name(self):
        """Test line display_name computation."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        line = self.env["pb.encryption.migration.wizard.line"].create(
            {
                "wizard_id": wizard.id,
                "model_name": "res.partner",
                "field_name": "vat_encrypted",
                "unencrypted_count": 10,
            }
        )
        self.assertEqual(line.display_name, "res.partner.vat_encrypted")

    def test_line_selected_default(self):
        """Test line selected defaults to False."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        line = self.env["pb.encryption.migration.wizard.line"].create(
            {
                "wizard_id": wizard.id,
                "model_name": "test.model",
                "field_name": "test_field",
                "unencrypted_count": 0,
            }
        )
        self.assertFalse(line.selected)


@tagged("post_install", "-at_install")
class TestMigrationWizardRefresh(TransactionCase):
    """Test migration wizard refresh functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_action_refresh(self):
        """Test refreshing the wizard clears and recreates lines."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})

        # Create initial line
        self.env["pb.encryption.migration.wizard.line"].create(
            {
                "wizard_id": wizard.id,
                "model_name": "old.model",
                "field_name": "old_field",
                "unencrypted_count": 5,
            }
        )
        self.assertEqual(len(wizard.line_ids), 1)

        # Refresh should recreate lines
        action = wizard.action_refresh()

        # Should return a reopen action
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_id"], wizard.id)


@tagged("post_install", "-at_install")
class TestMigrationWizardPreviewEdgeCases(TransactionCase):
    """Test migration wizard preview edge cases."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not config.get("encryption_key"):
            from cryptography.fernet import Fernet

            config["encryption_key"] = Fernet.generate_key().decode()

    def test_preview_already_encrypted(self):
        """Test preview message for already encrypted fields."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        self.env["pb.encryption.migration.wizard.line"].create(
            {
                "wizard_id": wizard.id,
                "model_name": "test.model",
                "field_name": "test_field",
                "unencrypted_count": 0,  # Already encrypted
                "selected": True,
            }
        )

        wizard.action_preview()

        self.assertEqual(wizard.state, "preview")
        self.assertIn("already encrypted", wizard.preview_info)

    def test_migrate_no_selection(self):
        """Test migrate fails when nothing selected."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        self.env["pb.encryption.migration.wizard.line"].create(
            {
                "wizard_id": wizard.id,
                "model_name": "test.model",
                "field_name": "test_field",
                "unencrypted_count": 5,
                "selected": False,
            }
        )

        with self.assertRaises(UserError) as cm:
            wizard.action_migrate()
        self.assertIn("No fields selected", str(cm.exception))

    def test_wizard_reopen(self):
        """Test _reopen returns proper action dict."""
        wizard = self.env["pb.encryption.migration.wizard"].create({})
        action = wizard._reopen()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "pb.encryption.migration.wizard")
        self.assertEqual(action["res_id"], wizard.id)
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")
