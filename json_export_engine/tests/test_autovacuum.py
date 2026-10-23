# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestJsonExportAutovacuum(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Create a minimal schema for logs
        cls.partner_exporter = cls.env["ir.exports"].create(
            {"name": "Autovacuum Test Export", "resource": "res.partner"}
        )
        cls.env["ir.exports.line"].create(
            {"export_id": cls.partner_exporter.id, "name": "name"}
        )
        cls.partner_model = cls.env.ref("base.model_res_partner")
        cls.schema = cls.env["json.export.schema"].create(
            {
                "name": "Autovacuum Test Schema",
                "model_id": cls.partner_model.id,
                "exporter_id": cls.partner_exporter.id,
                "domain": "[]",
                "record_limit": 10,
            }
        )

    def _create_log(self, age_days=0):
        """Create a log entry and backdate its create_date."""
        log = self.env["json.export.log"].create(
            {
                "schema_id": self.schema.id,
                "log_type": "api",
                "status": "success",
                "records_count": 1,
                "duration_ms": 10,
            }
        )
        if age_days:
            past = fields.Datetime.now() - timedelta(days=age_days)
            self.env.cr.execute(
                "UPDATE json_export_log SET create_date = %s WHERE id = %s",
                (past, log.id),
            )
            log.invalidate_recordset()
        return log

    def test_autovacuum_deletes_old_logs(self):
        """Logs older than retention are deleted."""
        old_log = self._create_log(age_days=100)
        recent_log = self._create_log(age_days=0)
        self.env["json.export.autovacuum"].autovacuum(days=90)
        self.assertFalse(old_log.exists())
        self.assertTrue(recent_log.exists())

    def test_autovacuum_preserves_recent_logs(self):
        """Logs within retention are preserved."""
        log = self._create_log(age_days=10)
        self.env["json.export.autovacuum"].autovacuum(days=30)
        self.assertTrue(log.exists())

    def test_autovacuum_reads_config_parameter(self):
        """Falls back to ir.config_parameter for retention days."""
        self.env["ir.config_parameter"].sudo().set_param(
            "json_export_engine.log_retention_days", "5"
        )
        old_log = self._create_log(age_days=10)
        recent_log = self._create_log(age_days=2)
        self.env["json.export.autovacuum"].autovacuum()
        self.assertFalse(old_log.exists())
        self.assertTrue(recent_log.exists())

    def test_autovacuum_days_zero_deletes_all(self):
        """days=0 deletes all log entries older than now."""
        self._create_log(age_days=1)
        self._create_log(age_days=2)
        deleted = self.env["json.export.autovacuum"].autovacuum(days=0)
        self.assertGreaterEqual(deleted, 2)

    def test_autovacuum_returns_count(self):
        """Returns the number of deleted records."""
        self._create_log(age_days=100)
        self._create_log(age_days=100)
        deleted = self.env["json.export.autovacuum"].autovacuum(days=90)
        self.assertEqual(deleted, 2)
