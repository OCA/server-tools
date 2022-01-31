# Copyright 2015 Therp BV <https://therp.nl>
# © 2018 Pieter Paulussen <pieter_paulussen@me.com>
# © 2021 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.modules.migration import load_script
from odoo.tests.common import TransactionCase

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


class AuditlogCommon(object):
    def test_LogCreation(self):
        """First test, caching some data."""

        self.groups_rule.subscribe()

        auditlog_log = self.env["auditlog.log"]
        group = self.env["res.groups"].create({"name": "testgroup1"})
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", group.id),
                ]
            ).ensure_one()
        )
        group.write({"name": "Testgroup1"})
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "write"),
                    ("res_id", "=", group.id),
                ]
            ).ensure_one()
        )
        group.unlink()
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "unlink"),
                    ("res_id", "=", group.id),
                ]
            ).ensure_one()
        )

    def test_LogCreation2(self):
        """Second test, using cached data of the first one."""

        self.groups_rule.subscribe()

        auditlog_log = self.env["auditlog.log"]
        testgroup2 = self.env["res.groups"].create({"name": "testgroup2"})
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", testgroup2.id),
                ]
            ).ensure_one()
        )

    def test_LogCreation3(self):
        """Third test, two groups, the latter being the parent of the former.
        Then we remove it right after (with (2, X) tuple) to test the creation
        of a 'write' log with a deleted resource (so with no text
        representation).
        """

        self.groups_rule.subscribe()
        auditlog_log = self.env["auditlog.log"]
        testgroup3 = testgroup3 = self.env["res.groups"].create({"name": "testgroup3"})
        testgroup4 = self.env["res.groups"].create(
            {"name": "testgroup4", "implied_ids": [(4, testgroup3.id)]}
        )
        testgroup4.write({"implied_ids": [(2, testgroup3.id)]})
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", testgroup3.id),
                ]
            ).ensure_one()
        )
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", testgroup4.id),
                ]
            ).ensure_one()
        )
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "write"),
                    ("res_id", "=", testgroup4.id),
                ]
            ).ensure_one()
        )

    def test_LogCreation4(self):
        """Fourth test, create several records at once (with create multi
        feature starting from Odoo 12) and check that the same number of logs
        has been generated.
        """

        self.groups_rule.subscribe()

        auditlog_log = self.env["auditlog.log"]
        groups_vals = [
            {"name": "testgroup1"},
            {"name": "testgroup3"},
            {"name": "testgroup2"},
        ]
        groups = self.env["res.groups"].create(groups_vals)
        # Ensure that the recordset returns is in the same order
        # than list of vals
        expected_names = ["testgroup1", "testgroup3", "testgroup2"]
        self.assertEqual(groups.mapped("name"), expected_names)

        logs = auditlog_log.search(
            [
                ("model_id", "=", self.groups_model_id),
                ("method", "=", "create"),
                ("res_id", "in", groups.ids),
            ]
        )
        self.assertEqual(len(logs), len(groups))

    def test_LogCreation5(self):
        """Fifth test, create a record and check that the same number of logs
        has been generated. And then delete it, check that it has created log
        with 0 fields updated.
        """
        self.groups_rule.subscribe()

        auditlog_log = self.env["auditlog.log"]
        testgroup5 = self.env["res.groups"].create({"name": "testgroup5"})
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", testgroup5.id),
                ]
            ).ensure_one()
        )
        testgroup5.unlink()
        log_record = auditlog_log.search(
            [
                ("model_id", "=", self.groups_model_id),
                ("method", "=", "unlink"),
                ("res_id", "=", testgroup5.id),
            ]
        ).ensure_one()
        self.assertTrue(log_record)
        if not self.groups_rule.capture_record:
            self.assertEqual(len(log_record.line_ids), 0)

    def test_LogCreation6(self):
        """Six test, create a record and check that the same number of logs
        has been generated. And then delete it, check that it has created log
        with x fields updated as per rule
        """
        self.groups_rule.subscribe()

        auditlog_log = self.env["auditlog.log"]
        testgroup6 = self.env["res.groups"].create({"name": "testgroup6"})
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", testgroup6.id),
                ]
            ).ensure_one()
        )
        testgroup6.unlink()
        log_record = auditlog_log.search(
            [
                ("model_id", "=", self.groups_model_id),
                ("method", "=", "unlink"),
                ("res_id", "=", testgroup6.id),
            ]
        ).ensure_one()
        self.assertTrue(log_record)
        if self.groups_rule.capture_record:
            self.assertTrue(len(log_record.line_ids) > 0)


class TestAuditlogFull(TransactionCase, AuditlogCommon):
    def setUp(self):
        super(TestAuditlogFull, self).setUp()
        self.groups_model_id = self.env.ref("base.model_res_groups").id
        self.groups_rule = self.env["auditlog.rule"].create(
            {
                "name": "testrule for groups",
                "model_id": self.groups_model_id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_type": "full",
            }
        )

    def tearDown(self):
        self.groups_rule.unlink()
        super(TestAuditlogFull, self).tearDown()


class TestAuditlogFast(TransactionCase, AuditlogCommon):
    def setUp(self):
        super(TestAuditlogFast, self).setUp()
        self.groups_model_id = self.env.ref("base.model_res_groups").id
        self.groups_rule = self.env["auditlog.rule"].create(
            {
                "name": "testrule for groups",
                "model_id": self.groups_model_id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_type": "fast",
            }
        )

    def tearDown(self):
        self.groups_rule.unlink()
        super(TestAuditlogFast, self).tearDown()


class TestFieldRemoval(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Clear all existing logging lines
        existing_audit_logs = cls.env["auditlog.log"].search([])
        existing_audit_logs.unlink()

        # Create a test model to remove
        cls.test_model = (
            cls.env["ir.model"]
            .sudo()
            .create(
                [{"name": "x_test_model", "model": "x_test.model", "state": "manual"}]
            )
        )

        # Create a test model field to remove
        cls.test_field = (
            cls.env["ir.model.fields"]
            .sudo()
            .create(
                [
                    {
                        "name": "x_test_field",
                        "field_description": "x_Test Field",
                        "model_id": cls.test_model.id,
                        "ttype": "char",
                        "state": "manual",
                    }
                ]
            )
        )
        # Setup auditlog rule
        cls.auditlog_rule = cls.env["auditlog.rule"].create(
            [
                {
                    "name": "test.model",
                    "model_id": cls.test_model.id,
                    "log_type": "fast",
                    "log_read": False,
                    "log_create": True,
                    "log_write": True,
                    "log_unlink": False,
                }
            ]
        )

        cls.auditlog_rule.subscribe()
        # Trigger log creation
        rec = cls.env["x_test.model"].create({"x_test_field": "test value"})
        rec.write({"x_test_field": "test value 2"})

        cls.logs = cls.env["auditlog.log"].search(
            [("res_id", "=", rec.id), ("model_id", "=", cls.test_model.id)]
        )

    def assert_values(self):
        """Assert that the denormalized field and model info is present
        on the auditlog records"""
        self.logs.refresh()
        self.assertEqual(self.logs[0].model_name, "x_test_model")
        self.assertEqual(self.logs[0].model_model, "x_test.model")

        log_lines = self.logs.mapped("line_ids")
        self.assertEqual(len(log_lines), 2)
        self.assertEqual(log_lines[0].field_name, "x_test_field")
        self.assertEqual(log_lines[0].field_description, "x_Test Field")

        self.auditlog_rule.refresh()
        self.assertEqual(self.auditlog_rule.model_name, "x_test_model")
        self.assertEqual(self.auditlog_rule.model_model, "x_test.model")

    def test_01_field_and_model_removal(self):
        """Test field and model removal to check auditlog line persistence"""
        self.assert_values()

        # Remove the field
        self.test_field.with_context(**{MODULE_UNINSTALL_FLAG: True}).unlink()
        self.assert_values()
        # The field should not be linked
        self.assertFalse(self.logs.mapped("line_ids.field_id"))

        # Remove the model
        self.test_model.with_context(**{MODULE_UNINSTALL_FLAG: True}).unlink()
        self.assert_values()

        # The model should not be linked
        self.assertFalse(self.logs.mapped("model_id"))
        # Assert rule values
        self.assertFalse(self.auditlog_rule.model_id)

    def test_02_migration(self):
        """Test the migration of the data model related to this feature"""
        # Drop the data model
        self.env.cr.execute(
            """ALTER TABLE auditlog_log
            DROP COLUMN model_name, DROP COLUMN model_model"""
        )
        self.env.cr.execute(
            """ALTER TABLE auditlog_rule
            DROP COLUMN model_name, DROP COLUMN model_model"""
        )
        self.env.cr.execute(
            """ALTER TABLE auditlog_log_line
            DROP COLUMN field_name, DROP COLUMN field_description"""
        )

        # Recreate the data model
        mod = load_script(
            "auditlog/migrations/14.0.1.1.0/pre-migration.py", "pre-migration"
        )
        mod.migrate(self.env.cr, "14.0.1.0.2")

        # Values are restored
        self.assert_values()

        # The migration script is tolerant if the data model is already in place
        mod.migrate(self.env.cr, "14.0.1.0.2")


class TestAuditlogFullCaptureRecord(TransactionCase, AuditlogCommon):
    def setUp(self):
        super(TestAuditlogFullCaptureRecord, self).setUp()
        self.groups_model_id = self.env.ref("base.model_res_groups").id
        self.groups_rule = self.env["auditlog.rule"].create(
            {
                "name": "testrule for groups with capture unlink record",
                "model_id": self.groups_model_id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_type": "full",
                "capture_record": True,
            }
        )

    def tearDown(self):
        self.groups_rule.unlink()
        super(TestAuditlogFullCaptureRecord, self).tearDown()
