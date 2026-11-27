# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class AuditLogRuleCommon(TransactionCase):
    """Rules must be subscribed in `setUp` or in the test itself, not in
    `setUpClass`: patched methods are reverted after each test."""

    @classmethod
    def create_rule(cls, vals):
        return cls.env["auditlog.rule"].with_context(tracking_disable=True).create(vals)

    def setUp(self):
        super().setUp()
        # A cleanup also runs when setUp fails after subscribing a rule,
        # unlike tearDown.
        self.addCleanup(self._unsubscribe_rules)

    def _unsubscribe_rules(self):
        for rule in self.env["auditlog.rule"].search([]):
            try:
                rule.set_to_draft()
            except KeyError:  # pragma: no cover
                continue  # Preexisting rule for model not loaded yet
        # Assert no patched methods remain
        for model_class in self.env.registry.values():
            for method in ["create", "read", "write", "unlink", "export_data"]:
                assert not hasattr(model_class, f"auditlog_ruled_{method}"), (
                    f"{model_class._name} {method} still patched"
                )
