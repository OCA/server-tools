# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAuditLog(TransactionCase):
    """Test audit log functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_user = cls.env.ref("base.user_admin")
        cls.AuditLog = cls.env["pb.encrypted.audit.log"]

    def test_create_audit_log(self):
        """Test creating audit log entry."""
        log = self.AuditLog.sudo().create(
            {
                "user_id": self.admin_user.id,
                "model_name": "res.partner",
                "field_name": "vat",
                "record_id": 1,
                "action": "decrypt",
            }
        )
        self.assertTrue(log.id)
        self.assertEqual(log.action, "decrypt")

    def test_audit_log_display_name(self):
        """Test audit log display_name computation."""
        log = self.AuditLog.sudo().create(
            {
                "user_id": self.admin_user.id,
                "model_name": "res.partner",
                "field_name": "vat",
                "record_id": 42,
                "action": "decrypt",
            }
        )
        self.assertIn(self.admin_user.name, log.display_name)
        self.assertIn("res.partner", log.display_name)
        self.assertIn("vat", log.display_name)
        self.assertIn("42", log.display_name)

    def test_audit_log_export_action(self):
        """Test audit log with export action."""
        log = self.AuditLog.sudo().create(
            {
                "user_id": self.admin_user.id,
                "model_name": "hr.employee",
                "field_name": "ssn",
                "record_id": 10,
                "action": "export",
            }
        )
        self.assertEqual(log.action, "export")

    def test_cleanup_old_logs_default(self):
        """Test cleanup with default retention from config parameter."""
        # Create old log entry
        old_date = datetime.now() - timedelta(days=100)
        log = self.AuditLog.sudo().create(
            {
                "user_id": self.admin_user.id,
                "model_name": "test.model",
                "field_name": "test_field",
                "record_id": 1,
                "action": "decrypt",
            }
        )
        # Manually set create_date to old date
        self.env.cr.execute(
            "UPDATE pb_encrypted_audit_log SET create_date = %s WHERE id = %s",
            (old_date, log.id),
        )

        # Set retention to 90 days (default)
        self.env["ir.config_parameter"].sudo().set_param(
            "encryption.audit_log_retention_days", "90"
        )

        count = self.AuditLog.sudo().cleanup_old_logs()
        self.assertGreaterEqual(count, 1)

        # Verify log is deleted
        self.assertFalse(self.AuditLog.sudo().browse(log.id).exists())

    def test_cleanup_old_logs_custom_days(self):
        """Test cleanup with custom days parameter."""
        # Create log from 10 days ago
        old_date = datetime.now() - timedelta(days=10)
        log = self.AuditLog.sudo().create(
            {
                "user_id": self.admin_user.id,
                "model_name": "test.model",
                "field_name": "test_field",
                "record_id": 1,
                "action": "decrypt",
            }
        )
        self.env.cr.execute(
            "UPDATE pb_encrypted_audit_log SET create_date = %s WHERE id = %s",
            (old_date, log.id),
        )

        # Cleanup logs older than 5 days
        count = self.AuditLog.sudo().cleanup_old_logs(days=5)
        self.assertGreaterEqual(count, 1)

    def test_cleanup_preserves_recent_logs(self):
        """Test that cleanup preserves recent logs."""
        # Create recent log
        log = self.AuditLog.sudo().create(
            {
                "user_id": self.admin_user.id,
                "model_name": "test.model",
                "field_name": "test_field",
                "record_id": 1,
                "action": "decrypt",
            }
        )

        # Cleanup logs older than 90 days
        self.AuditLog.sudo().cleanup_old_logs(days=90)

        # Recent log should still exist
        self.assertTrue(self.AuditLog.sudo().browse(log.id).exists())

    def test_get_access_report_no_filters(self):
        """Test access report without filters."""
        # Create some logs
        self.AuditLog.sudo().create(
            {
                "user_id": self.admin_user.id,
                "model_name": "res.partner",
                "field_name": "vat",
                "record_id": 1,
                "action": "decrypt",
            }
        )
        logs = self.AuditLog.sudo().get_access_report()
        self.assertTrue(len(logs) >= 1)

    def test_get_access_report_with_model_filter(self):
        """Test access report filtered by model."""
        self.AuditLog.sudo().create(
            {
                "user_id": self.admin_user.id,
                "model_name": "res.partner",
                "field_name": "vat",
                "record_id": 1,
                "action": "decrypt",
            }
        )
        self.AuditLog.sudo().create(
            {
                "user_id": self.admin_user.id,
                "model_name": "hr.employee",
                "field_name": "ssn",
                "record_id": 2,
                "action": "decrypt",
            }
        )

        logs = self.AuditLog.sudo().get_access_report(model_name="res.partner")
        for log in logs:
            self.assertEqual(log.model_name, "res.partner")

    def test_get_access_report_with_user_filter(self):
        """Test access report filtered by user."""
        self.AuditLog.sudo().create(
            {
                "user_id": self.admin_user.id,
                "model_name": "res.partner",
                "field_name": "vat",
                "record_id": 1,
                "action": "decrypt",
            }
        )

        logs = self.AuditLog.sudo().get_access_report(user_id=self.admin_user.id)
        for log in logs:
            self.assertEqual(log.user_id.id, self.admin_user.id)

    def test_get_access_report_with_date_range(self):
        """Test access report filtered by date range."""
        self.AuditLog.sudo().create(
            {
                "user_id": self.admin_user.id,
                "model_name": "res.partner",
                "field_name": "vat",
                "record_id": 1,
                "action": "decrypt",
            }
        )

        date_from = datetime.now() - timedelta(days=1)
        date_to = datetime.now() + timedelta(days=1)

        logs = self.AuditLog.sudo().get_access_report(
            date_from=date_from, date_to=date_to
        )
        self.assertTrue(len(logs) >= 1)


@tagged("post_install", "-at_install")
class TestAuditLogRetentionConfig(TransactionCase):
    """Test audit log retention configuration."""

    def test_retention_from_config_parameter(self):
        """Test that retention reads from config parameter."""
        self.env["ir.config_parameter"].sudo().set_param(
            "encryption.audit_log_retention_days", "30"
        )

        AuditLog = self.env["pb.encrypted.audit.log"]
        # Create log from 40 days ago
        old_date = datetime.now() - timedelta(days=40)
        log = AuditLog.sudo().create(
            {
                "user_id": self.env.ref("base.user_admin").id,
                "model_name": "test.model",
                "field_name": "test_field",
                "record_id": 1,
                "action": "decrypt",
            }
        )
        self.env.cr.execute(
            "UPDATE pb_encrypted_audit_log SET create_date = %s WHERE id = %s",
            (old_date, log.id),
        )

        # Should delete because 40 > 30 days
        count = AuditLog.sudo().cleanup_old_logs()
        self.assertGreaterEqual(count, 1)

    def test_retention_default_when_not_configured(self):
        """Test default 90 days when parameter not set."""
        # Remove parameter if exists
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .search([("key", "=", "encryption.audit_log_retention_days")])
        )
        param.unlink()

        AuditLog = self.env["pb.encrypted.audit.log"]
        # Create log from 80 days ago (should NOT be deleted with 90 day default)
        old_date = datetime.now() - timedelta(days=80)
        log = AuditLog.sudo().create(
            {
                "user_id": self.env.ref("base.user_admin").id,
                "model_name": "test.model",
                "field_name": "test_field",
                "record_id": 1,
                "action": "decrypt",
            }
        )
        self.env.cr.execute(
            "UPDATE pb_encrypted_audit_log SET create_date = %s WHERE id = %s",
            (old_date, log.id),
        )

        # Run cleanup
        AuditLog.sudo().cleanup_old_logs()

        # Log should still exist (80 < 90 days)
        self.assertTrue(AuditLog.sudo().browse(log.id).exists())
