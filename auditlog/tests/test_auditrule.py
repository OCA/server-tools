from odoo.tests.common import TransactionCase


class TestAuditlogRule(TransactionCase):
    def setUp(self):
        super(TestAuditlogRule, self).setUp()
        self.groups_model_id = self.env.ref("base.model_res_groups").id

    def test_create_auto_subscribe(self):
        """Link to quick view (action_id) should also be created with new rule"""
        groups_rule = self.env["auditlog.rule"].create(
            {
                "name": "testrule for groups",
                "model_id": self.groups_model_id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "state": "subscribed",
                "log_type": "full",
            }
        )
        self.assertTrue(groups_rule.action_id)

    def test_auto_subscribe_is_reentrant(self):
        """Quick view link should not change"""
        groups_rule = self.env["auditlog.rule"].create(
            {
                "name": "testrule for groups",
                "model_id": self.groups_model_id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "state": "subscribed",
                "log_type": "full",
            }
        )
        action_id = groups_rule.action_id
        groups_rule.subscribe()
        self.assertEqual(groups_rule.action_id, action_id)
