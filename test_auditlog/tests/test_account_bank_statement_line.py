from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.auditlog.tests.common import AuditLogRuleCommon


@tagged("post_install", "-at_install")
class TestAccountBankStatementLine(AccountTestInvoicingCommon, AuditLogRuleCommon):
    def setUp(self):
        super().setUp()
        self.rule = self.env["auditlog.rule"].create(
            {
                "name": __name__,
                "model_id": self.env.ref("account.model_account_move").id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_type": "full",
            }
        )
        self.rule.subscribe()

    def test_create_statement_line(self):
        """Statement line can be created with logging on journal entries enabled.

        Because we swap out the cache when fetching previous values during full
        logging using the ThrowAwayCache, some values that are assumed by
        compute methods (c.q. 'date' in account.bank.statement.line's
        _compute_internal_index) might be missing. If a recompute of those fields
        is inadvertently triggered when using the ThrowAwayCache, the missing
        values will raise an exception (in this case: `AttributeError: 'bool'
        object has no attribute 'strftime'`). This test verifies that the queued
        recomputes are consistent with the values in the cache such that this
        exception does not occur.
        """
        partner = self.env["res.partner"].create({"name": "test"})
        stmt = self.env["account.bank.statement"].create(
            {"journal_id": self.company_data["default_journal_bank"].id}
        )
        line = self.env["account.bank.statement.line"].create(
            {
                "date": "2023-04-01",
                "account_number": "NL45 TRIO 0198100000",
                "amount": 5.75,
                "journal_id": self.company_data["default_journal_bank"].id,
                "payment_ref": "1234",
                "partner_id": partner.id,
                "statement_id": stmt.id,
            },
        )
        line.flush_recordset()
