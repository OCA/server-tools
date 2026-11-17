# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.auditlog.tests.common import AuditLogRuleCommon


@tagged("post_install", "-at_install")
class TestAuditlogRuleAuthMethod(AuditLogRuleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.Log = cls.env["auditlog.log"]
        cls.Category = cls.env["res.partner.category"]
        # Instances
        cls.rule = cls.create_rule(
            {
                "name": "Auth method rule",
                "model_id": cls.env.ref("base.model_res_partner_category").id,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_type": "full",
            }
        )
        # Existing instances
        cls.server_method = cls.env.ref("auditlog_auth_method.auth_method_server")
        cls.api_key_method = cls.env.ref("auditlog_auth_method.auth_method_rpc_api_key")

    def setUp(self):
        super().setUp()
        self.addCleanup(self.registry.clear_cache)

    def _get_logs(self, record):
        return self.Log.search(
            [("model_id", "=", self.rule.model_id.id), ("res_id", "=", record.id)]
        )

    def test_log_without_filter(self):
        self.rule.subscribe()
        category = self.Category.create({"name": "No filter"})
        category.name = "No filter updated"
        logs = self._get_logs(category)
        self.assertEqual(sorted(logs.mapped("method")), ["create", "write"])
        self.assertEqual(logs.auth_method_id, self.server_method)
        self.assertFalse(any(logs.mapped("auth_api_key_name")))

    def test_log_filtered_in(self):
        self.rule.auth_method_ids = self.server_method
        self.rule.subscribe()
        category = self.Category.create({"name": "Filtered in"})
        self.assertEqual(self._get_logs(category).auth_method_id, self.server_method)

    def test_log_filtered_out(self):
        self.rule.auth_method_ids = self.api_key_method
        self.rule.subscribe()
        category = self.Category.create({"name": "Filtered out"})
        category.name = "Filtered out updated"
        category_id = category.id
        category.unlink()
        self.assertFalse(
            self.Log.search(
                [("model_id", "=", self.rule.model_id.id), ("res_id", "=", category_id)]
            )
        )

    def test_filter_change_on_subscribed_rule(self):
        self.rule.auth_method_ids = self.api_key_method
        self.rule.subscribe()
        filtered_out = self.Category.create({"name": "Before change"})
        self.rule.auth_method_ids |= self.server_method
        filtered_in = self.Category.create({"name": "After change"})
        self.assertFalse(self._get_logs(filtered_out))
        self.assertTrue(self._get_logs(filtered_in))

    def test_gate_keeps_method_attributes(self):
        self.rule.unsubscribe()
        model_class = type(self.Category)
        original_create = model_class.create
        self.rule.subscribe()
        self.assertEqual(model_class.create._api, "model_create")
        self.assertIs(model_class.create.origin, original_create)
        self.rule.unsubscribe()
        self.assertIs(model_class.create, original_create)
