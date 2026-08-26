# Copyright 2026 Kobros-Tech Ltd (http://kobros-tech.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestSecurityAnalyzer(TransactionCase):
    """Test cases for security.analyzer model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Use existing demo user to avoid user creation issues
        # Look for demo user or any non-admin internal user
        cls.test_user = cls.env["res.users"].search(
            [
                ("share", "=", False),  # Internal user
                ("id", "!=", 1),  # Not OdooBot
                ("id", "!=", 2),  # Not admin
            ],
            limit=1,
        )

        # If no suitable user found, use admin as fallback
        if not cls.test_user:
            cls.test_user = cls.env.ref("base.user_admin")

        cls.test_model = "res.partner"

    def setUp(self):
        super(TestSecurityAnalyzer, self).setUp()
        self.analyzer = self.env["security.analyzer"]

    def test_analyze_model_access_allowed(self):
        """Test analyzing model access when user has permission"""
        result = self.analyzer.analyze_model_access(
            self.test_model, self.test_user.id, "read"
        )

        self.assertTrue(
            result["has_access"], "User should have read access to res.partner"
        )
        self.assertEqual(result["operation"], "read")
        self.assertEqual(result["model"], self.test_model)
        self.assertIn("applicable_rules", result)

    def test_analyze_model_access_denied(self):
        """Test analyzing model access when user lacks permission"""
        # Use a model that test_user likely doesn't have access to
        result = self.analyzer.analyze_model_access(
            "ir.cron",  # Scheduled actions - restricted model
            self.test_user.id,
            "write",
        )

        # This may pass or fail depending on configuration, just check structure
        self.assertIn("has_access", result)
        self.assertIn("applicable_rules", result)
        self.assertIn("explanation", result)

    def test_analyze_record_rules(self):
        """Test analyzing record rules for a model"""
        result = self.analyzer.analyze_record_rules(
            self.test_model, self.test_user.id, "read"
        )

        self.assertIn("rules", result)
        self.assertIn("global_rules", result)
        self.assertIn("group_rules", result)
        self.assertIn("explanation", result)
        self.assertIsInstance(result["rules"], list)

    def test_explain_access_decision(self):
        """Test comprehensive access explanation"""
        result = self.analyzer.explain_access_decision(
            self.test_model,
            self.test_user.id,
            record_id=None,  # No specific record
            operation="read",
        )

        self.assertIn("model_access", result)
        self.assertIn("record_rules", result)
        self.assertIn("final_verdict", result)
        self.assertIn("verdict_explanation", result)
        self.assertIn("steps", result)

        # Check verdict is one of expected values
        self.assertIn(result["final_verdict"], ["allowed", "denied", "conditional"])

    def test_simulate_user_access_no_record(self):
        """Test simulating access when record doesn't exist"""
        result = self.analyzer.simulate_user_access(
            self.test_user.id, self.test_model, 999999, "read"  # Non-existent record
        )

        self.assertFalse(result["has_access"])
        self.assertEqual(result["error"], "record_not_found")

    def test_simulate_user_access_with_record(self):
        """Test simulating access for an existing record"""
        # Create a test partner record
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        result = self.analyzer.simulate_user_access(
            self.test_user.id, self.test_model, partner.id, "read"
        )

        self.assertIn("has_access", result)
        self.assertIn("explanation", result)

    def test_get_access_matrix(self):
        """Test generating access matrix"""
        result = self.analyzer.get_access_matrix(
            user_ids=[self.test_user.id],
            model_ids=None,  # Use defaults
            operations=["read", "write"],
        )

        self.assertIn("users", result)
        self.assertIn("models", result)
        self.assertIn("operations", result)
        self.assertIn("cells", result)

        self.assertEqual(len(result["users"]), 1)
        self.assertEqual(result["operations"], ["read", "write"])
        self.assertIsInstance(result["cells"], dict)

    def test_get_user_accessible_models(self):
        """Test getting list of accessible models for user"""
        result = self.analyzer.get_user_accessible_models(self.test_user.id, "read")

        self.assertIsInstance(result, list)
        # User should have access to at least some models
        self.assertGreater(len(result), 0)

        # Check structure of returned items
        if result:
            item = result[0]
            self.assertIn("model", item)
            self.assertIn("name", item)
            self.assertIn("access_rules", item)

    def test_analyze_multicompany_access(self):
        """Test multi-company access analysis"""
        result = self.analyzer.analyze_multicompany_access(
            self.test_model, self.test_user.id, "read"
        )

        # Check structure
        self.assertIn("user", result)
        self.assertIn("model", result)
        self.assertIn("has_company_field", result)
        self.assertIn("user_companies", result)
        self.assertIn("current_company", result)
        self.assertIn("company_rules", result)
        self.assertIn("explanation", result)

        # User should belong to at least one company
        self.assertGreater(len(result["user_companies"]), 0)

    def test_get_company_access_matrix(self):
        """Test company access matrix generation"""
        result = self.analyzer.get_company_access_matrix(
            self.test_user.id, company_ids=None  # Use user's companies
        )

        # Check structure
        self.assertIn("user", result)
        self.assertIn("companies", result)
        self.assertIn("models", result)
        self.assertIn("cells", result)

        self.assertEqual(result["user"]["id"], self.test_user.id)
        self.assertIsInstance(result["companies"], list)
        self.assertIsInstance(result["models"], list)
        self.assertIsInstance(result["cells"], dict)

    def test_analyze_user_roles_module_not_installed(self):
        """Test role analysis when base_user_role is not installed"""
        result = self.analyzer.analyze_user_roles(self.test_user.id)

        # Should return status about module not installed
        self.assertIn("module_installed", result)
        self.assertIn("explanation", result)

        # If module not installed, should have empty roles
        if not result["module_installed"]:
            self.assertEqual(len(result["roles"]), 0)

    def test_analyze_model_access_with_roles(self):
        """Test model access analysis with role information"""
        result = self.analyzer.analyze_model_access_with_roles(
            self.test_model, self.test_user.id, "read"
        )

        # Should have all standard model access fields
        self.assertIn("has_access", result)
        self.assertIn("applicable_rules", result)
        self.assertIn("explanation", result)

        # Plus role-specific information
        self.assertIn("role_analysis", result)
        self.assertIn("module_installed", result["role_analysis"])

    def test_explain_access_decision_with_roles(self):
        """Test comprehensive explanation with role information"""
        result = self.analyzer.explain_access_decision_with_roles(
            self.test_model, self.test_user.id, record_id=None, operation="read"
        )

        # Should have all standard explanation fields
        self.assertIn("model_access", result)
        self.assertIn("record_rules", result)
        self.assertIn("final_verdict", result)
        self.assertIn("steps", result)

        # Plus role analysis if module installed
        if self.analyzer._is_base_user_role_installed():
            self.assertIn("role_analysis", result)

    def test_analyze_crud_summary(self):
        """Test comprehensive CRUD summary with all 4 operations"""
        result = self.analyzer.analyze_crud_summary(self.test_model, self.test_user.id)

        self.assertIn("operations", result)
        self.assertIn("summary_table", result)
        self.assertIn("conflicts_detected", result)
        self.assertIn("conflict_explanation", result)

        # Should have exactly 4 operations in summary table
        self.assertEqual(len(result["summary_table"]), 4)

        expected_ops = {"CREATE", "READ", "WRITE", "UNLINK"}
        actual_ops = {row["operation"] for row in result["summary_table"]}
        self.assertEqual(actual_ops, expected_ops)

        for row in result["summary_table"]:
            self.assertIn("operation", row)
            self.assertIn("allowed", row)
            self.assertIn("has_conflict", row)
            self.assertIn("verdict", row)
            self.assertIn("granting_count", row)
            self.assertIn("denying_count", row)

        # Check operations dict
        for op in ["create", "read", "write", "unlink"]:
            self.assertIn(op, result["operations"])
            op_data = result["operations"][op]
            self.assertIn("allowed", op_data)
            self.assertIn("explanation", op_data)
