from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.auditlog.tests.common import AuditLogRuleCommon


@tagged("post_install", "-at_install")
class TestPaymentResidual(AccountTestInvoicingCommon, AuditLogRuleCommon):
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
        self.rule.set_to_confirmed()

    def test_register_payment_computes_residual(self):
        """Payment lines keep their stored computed values with a full rule.

        With a full-log rule on account.move, the swapped-cache reads of the
        log diff must not cause the pending recomputations of the payment
        lines' stored computed fields to be lost, or those columns end up
        NULL in the database (issue #3635: the payment is then never offered
        as an outstanding credit on the invoice).
        """
        invoice = self.init_invoice("out_invoice", products=self.product_a, post=True)
        wizard = (
            self.env["account.payment.register"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"journal_id": self.company_data["default_journal_bank"].id})
        )
        payments = wizard._create_payments()
        self.env.flush_all()
        self.env.cr.execute(
            """
            SELECT id, amount_residual, amount_residual_currency, reconciled
            FROM account_move_line
            WHERE move_id = %s
            """,
            (payments.move_id.id,),
        )
        rows = self.env.cr.fetchall()
        self.assertTrue(rows)
        for line_id, residual, residual_currency, reconciled in rows:
            self.assertIsNotNone(residual, f"line {line_id}: amount_residual is NULL")
            self.assertIsNotNone(
                residual_currency,
                f"line {line_id}: amount_residual_currency is NULL",
            )
            self.assertIsNotNone(reconciled, f"line {line_id}: reconciled is NULL")
