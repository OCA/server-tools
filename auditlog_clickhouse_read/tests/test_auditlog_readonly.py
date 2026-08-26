# Copyright (C) 2026 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.auditlog_clickhouse_read.models.auditlog_readonly import (
    _is_clickhouse_readonly_mode,
)

from .common import AuditlogClickhouseReadCommon


@tagged("-at_install", "post_install")
class TestAuditlogClickhouseReadonly(AuditlogClickhouseReadCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env.ref("base.model_res_partner")
        cls.name_field = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "name")],
            limit=1,
        )

    def _create_log(self):
        return (
            self.env["auditlog.log"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "name": "Readonly test log",
                    "model_id": self.partner_model.id,
                    "res_id": 1,
                    "user_id": self.env.user.id,
                    "method": "write",
                }
            )
        )

    def _create_log_line(self, log):
        return (
            self.env["auditlog.log.line"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "log_id": log.id,
                    "field_id": self.name_field.id,
                    "old_value_text": "old",
                    "new_value_text": "new",
                }
            )
        )

    def test_01_is_clickhouse_readonly_mode_true(self):
        with patch.object(
            type(self.env["auditlog.clickhouse.config"]),
            "_get_auditlog_read_mode",
            autospec=True,
            return_value="fdw",
        ):
            self.assertTrue(_is_clickhouse_readonly_mode(self.env))

    def test_02_is_clickhouse_readonly_mode_false(self):
        with patch.object(
            type(self.env["auditlog.clickhouse.config"]),
            "_get_auditlog_read_mode",
            autospec=True,
            return_value="postgres",
        ):
            self.assertFalse(_is_clickhouse_readonly_mode(self.env))

    def test_03_auditlog_log_create_blocked(self):
        with patch(
            "odoo.addons.auditlog_clickhouse_read.models.auditlog_readonly."
            "_is_clickhouse_readonly_mode",
            return_value=True,
        ):
            with self.assertRaises(UserError):
                self.env["auditlog.log"].create(
                    {
                        "name": "Blocked log",
                        "model_id": self.partner_model.id,
                        "res_id": 1,
                        "user_id": self.env.user.id,
                        "method": "write",
                    }
                )

    def test_04_auditlog_log_write_blocked(self):
        log = self._create_log()

        with patch(
            "odoo.addons.auditlog_clickhouse_read.models.auditlog_readonly."
            "_is_clickhouse_readonly_mode",
            return_value=True,
        ):
            with self.assertRaises(UserError):
                log.write({"name": "blocked"})

    def test_05_auditlog_log_unlink_blocked(self):
        log = self._create_log()

        with patch(
            "odoo.addons.auditlog_clickhouse_read.models.auditlog_readonly."
            "_is_clickhouse_readonly_mode",
            return_value=True,
        ):
            with self.assertRaises(UserError):
                log.unlink()

    def test_06_auditlog_log_line_create_blocked(self):
        log = self._create_log()

        with patch(
            "odoo.addons.auditlog_clickhouse_read.models.auditlog_readonly."
            "_is_clickhouse_readonly_mode",
            return_value=True,
        ):
            with self.assertRaises(UserError):
                self.env["auditlog.log.line"].create(
                    {
                        "log_id": log.id,
                        "field_id": self.name_field.id,
                        "old_value_text": "old",
                        "new_value_text": "new",
                    }
                )

    def test_07_auditlog_log_line_write_blocked(self):
        log = self._create_log()
        line = self._create_log_line(log)

        with patch(
            "odoo.addons.auditlog_clickhouse_read.models.auditlog_readonly."
            "_is_clickhouse_readonly_mode",
            return_value=True,
        ):
            with self.assertRaises(UserError):
                line.write({"new_value_text": "blocked"})

    def test_08_auditlog_log_line_unlink_blocked(self):
        log = self._create_log()
        line = self._create_log_line(log)

        with patch(
            "odoo.addons.auditlog_clickhouse_read.models.auditlog_readonly."
            "_is_clickhouse_readonly_mode",
            return_value=True,
        ):
            with self.assertRaises(UserError):
                line.unlink()
