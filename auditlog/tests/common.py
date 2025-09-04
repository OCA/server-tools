from odoo.tests.common import TransactionCase


class AuditLogRuleCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.models = set()

    @classmethod
    def create_rule(cls, vals):
        rule = cls.env["auditlog.rule"].with_context(tracking_disable=True).create(vals)
        # Keep track of patched models
        cls.models |= {rule.model_id.model}
        return rule

    @classmethod
    def tearDownClass(cls):
        cls.env["auditlog.rule"].search([]).unsubscribe()
        # Assert no patched methods remain
        for model in cls.models:
            for method in ["create", "read", "write", "unlink"]:
                assert not hasattr(
                    getattr(cls.env[model], method), "origin"
                ), f"{model} {method} still patched"
        super().tearDownClass()
