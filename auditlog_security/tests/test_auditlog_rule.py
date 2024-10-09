# Copyright 2024 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from psycopg2.errors import UniqueViolation

from odoo.tests.common import TransactionCase


class TestAuditlogRule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestAuditlogRule, cls).setUpClass()

        cls.model = cls.env["ir.model"].create(
            {
                "name": "Test Model",
                "model": "x_test_model",
            }
        )
        cls.rule = cls.env["auditlog.rule"].create(
            {
                "name": "Test Rule",
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
        cls.access_rule = cls.env["auditlog.line.access.rule"].create(
            {
                "name": "Access Rule",
                "auditlog_rule_id": cls.rule.id,
                "field_ids": [(6, 0, [cls.field.id])],
            }
        )

    def test_unique_model_constraint(self):
        """Test unique constraint on model_id field"""

        # Attempting to create a rule with the same
        # model_id should raise a UniqueViolation error

        with self.assertRaises(UniqueViolation):
            self.env["auditlog.rule"].create(
                {
                    "name": "Duplicate Rule",
                    "model_id": self.model.id,
                }
            )

    def test_get_field_names_of_rule(self):
        """Test cached method _get_field_names_of_rule"""
        field_names = self.rule._get_field_names_of_rule(self.model.model)
        self.assertIn(
            self.field.name,
            field_names,
            f"Expected field '{self.field.name}' not found in field names: {field_names}",
        )

    def test_get_log_selected_fields_only(self):
        """Test cached method _get_log_selected_fields_only"""
        log_selected = self.rule._get_log_selected_fields_only(self.model.model)
        self.assertTrue(log_selected)

    def test_get_auditlog_fields(self):
        """Test get_auditlog_fields filtering of fields"""
        fields = self.rule.get_auditlog_fields(self.env["x_test_model"])
        self.assertIn(
            self.field.name,
            fields,
            f"Expected field '{self.field.name}' not found in auditlog fields: {fields}",
        )

    def test_write_clears_cache(self):
        """Test that writing specific fields clears the cache"""
        # Clear cache to ensure fresh data is fetched
        self.env.cache.clear()

        # Fetch initial field names to ensure cache is populated
        initial_field_names = self.rule._get_field_names_of_rule(self.model.model)

        # Assert that the cache was populated correctly
        self.assertIn(
            self.field.name,
            initial_field_names,
            "Cache not populated correctly before write.",
        )

        # Write to the rule to trigger cache invalidation
        self.rule.write({"log_selected_fields_only": False})

        # Clear cache to force the method to re-evaluate
        self.env.cache.clear()

        # Fetch updated field names to ensure cache was cleared and repopulated
        updated_field_names = self.rule._get_field_names_of_rule(self.model.model)

        # Assert that the cache was updated correctly
        self.assertIn(
            self.field.name,
            updated_field_names,
            "Cache not updated correctly after write.",
        )
        self.assertEqual(
            updated_field_names,
            initial_field_names,
            "Cache should be recalculated and match expected values.",
        )

    def test_onchange_model_id(self):
        """Test that related access rules are removed when model_id is changed"""
        access_rule = self.env["auditlog.line.access.rule"].create(
            {
                "name": "Access Rule",
                "auditlog_rule_id": self.rule.id,
            }
        )
        self.assertTrue(access_rule.exists())
        self.rule.onchange_model_id()
        self.assertFalse(access_rule.exists())

    def test_create_server_action(self):
        """Test the creation of server action linked to the audit log rule"""
        action = self.rule._create_server_action()
        self.assertTrue(action)
        self.assertEqual(self.rule.server_action_id, action)

    def test_subscribe_method(self):
        """Test the subscribe method with rule regeneration and server action creation"""
        action_count_before = self.env["ir.actions.server"].search_count([])
        self.rule.subscribe()
        action_count_after = self.env["ir.actions.server"].search_count([])
        self.assertGreater(action_count_after, action_count_before)

    def test_unsubscribe_method(self):
        """Test the unsubscribe method with server action deletion"""
        self.rule.subscribe()
        server_action = self.rule.server_action_id
        self.assertTrue(server_action.exists())
        self.rule.unsubscribe()
        self.assertFalse(server_action.exists())
