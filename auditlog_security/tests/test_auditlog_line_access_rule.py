# Copyright 2024 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAuditlogLineAccessRule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestAuditlogLineAccessRule, cls).setUpClass()
        cls.group_user = cls.env.ref("base.group_user")
        cls.model = cls.env["ir.model"].create(
            {
                "name": "Test Model",
                "model": "x_test_model_2",
            }
        )
        cls.auditlog_rule = cls.env["auditlog.rule"].create(
            {
                "name": "Test Auditlog Rule",
                "model_id": cls.model.id,
            }
        )
        cls.field = cls.env["ir.model.fields"].create(
            {
                "name": "x_test_field",
                "model_id": cls.model.id,
                "field_description": "Test Field",
                "ttype": "char",
            }
        )

    def test_create_auditlog_line_access_rule(self):
        """Test the creation of an auditlog line access rule"""
        rule = self.env["auditlog.line.access.rule"].create(
            {
                "name": "Test Rule",
                "auditlog_rule_id": self.auditlog_rule.id,
                "field_ids": [(6, 0, [self.field.id])],
            }
        )
        self.assertTrue(rule)

    def test_write_auditlog_line_access_rule(self):
        """Test writing to an auditlog line access rule"""
        rule = self.env["auditlog.line.access.rule"].create(
            {
                "name": "Test Rule",
                "auditlog_rule_id": self.auditlog_rule.id,
            }
        )
        rule.write(
            {
                "field_ids": [(6, 0, [self.field.id])],
            }
        )
        self.assertIn(self.field, rule.field_ids)
