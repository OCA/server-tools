from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.auditlog.tests.common import AuditLogRuleCommon


@tagged("post_install", "-at_install")
class TestAccountMoveReverse(AccountTestInvoicingCommon, AuditLogRuleCommon):
    @classmethod
    def setUpClass(cls):
        # Class setup taken from account/tests/test_account_move_in_invoice.py
        super().setUpClass()

        cls.other_currency = cls.setup_other_currency("EUR")

        cls.invoice = cls.init_invoice(
            "in_invoice", products=cls.product_a + cls.product_b
        )

        cls.product_line_vals_1 = {
            "name": "product_a",
            "product_id": cls.product_a.id,
            "account_id": cls.product_a.property_account_expense_id.id,
            "partner_id": cls.partner_a.id,
            "product_uom_id": cls.product_a.uom_id.id,
            "quantity": 1.0,
            "discount": 0.0,
            "price_unit": 800.0,
            "price_subtotal": 800.0,
            "price_total": 920.0,
            "tax_ids": cls.product_a.supplier_taxes_id.ids,
            "tax_line_id": False,
            "currency_id": cls.company_data["currency"].id,
            "amount_currency": 800.0,
            "debit": 800.0,
            "credit": 0.0,
            "date_maturity": False,
        }
        cls.product_line_vals_2 = {
            "name": "product_b",
            "product_id": cls.product_b.id,
            "account_id": cls.product_b.property_account_expense_id.id,
            "partner_id": cls.partner_a.id,
            "product_uom_id": cls.product_b.uom_id.id,
            "quantity": 1.0,
            "discount": 0.0,
            "price_unit": 160.0,
            "price_subtotal": 160.0,
            "price_total": 208.0,
            "tax_ids": cls.product_b.supplier_taxes_id.ids,
            "tax_line_id": False,
            "currency_id": cls.company_data["currency"].id,
            "amount_currency": 160.0,
            "debit": 160.0,
            "credit": 0.0,
            "date_maturity": False,
        }
        cls.tax_line_vals_1 = {
            "name": cls.tax_purchase_a.name,
            "product_id": False,
            "account_id": cls.company_data["default_account_tax_purchase"].id,
            "partner_id": cls.partner_a.id,
            "product_uom_id": False,
            "quantity": False,
            "discount": 0.0,
            "price_unit": 0.0,
            "price_subtotal": 0.0,
            "price_total": 0.0,
            "tax_ids": [],
            "tax_line_id": cls.tax_purchase_a.id,
            "currency_id": cls.company_data["currency"].id,
            "amount_currency": 144.0,
            "debit": 144.0,
            "credit": 0.0,
            "date_maturity": False,
        }
        cls.tax_line_vals_2 = {
            "name": cls.tax_purchase_b.name,
            "product_id": False,
            "account_id": cls.company_data["default_account_tax_purchase"].id,
            "partner_id": cls.partner_a.id,
            "product_uom_id": False,
            "quantity": False,
            "discount": 0.0,
            "price_unit": 0.0,
            "price_subtotal": 0.0,
            "price_total": 0.0,
            "tax_ids": [],
            "tax_line_id": cls.tax_purchase_b.id,
            "currency_id": cls.company_data["currency"].id,
            "amount_currency": 24.0,
            "debit": 24.0,
            "credit": 0.0,
            "date_maturity": False,
        }
        cls.term_line_vals_1 = {
            "name": False,
            "product_id": False,
            "account_id": cls.company_data["default_account_payable"].id,
            "partner_id": cls.partner_a.id,
            "product_uom_id": False,
            "quantity": False,
            "discount": 0.0,
            "price_unit": 0.0,
            "price_subtotal": 0.0,
            "price_total": 0.0,
            "tax_ids": [],
            "tax_line_id": False,
            "currency_id": cls.company_data["currency"].id,
            "amount_currency": -1128.0,
            "debit": 0.0,
            "credit": 1128.0,
            "date_maturity": fields.Date.from_string("2019-01-01"),
        }
        cls.move_vals = {
            "partner_id": cls.partner_a.id,
            "currency_id": cls.company_data["currency"].id,
            "journal_id": cls.company_data["default_journal_purchase"].id,
            "date": fields.Date.from_string("2019-01-01"),
            "fiscal_position_id": False,
            "payment_reference": False,
            "invoice_payment_term_id": cls.pay_terms_a.id,
            "amount_untaxed": 960.0,
            "amount_tax": 168.0,
            "amount_total": 1128.0,
        }
        cls.env.user.groups_id += cls.env.ref("uom.group_uom")

    def setUp(self):
        super().setUp()
        rules = self.env["auditlog.rule"].search([])
        rules.unsubscribe()
        rules.unlink()
        self.rule = self.env["auditlog.rule"].create(
            {
                "name": __name__,
                "model_id": self.env.ref("account.model_account_move_line").id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_type": "full",
            }
        )
        self.rule.subscribe()

    def test_in_invoice_stored_related_field(self):
        """Stored related fields are computed properly"""
        self.invoice.name = "TEST"
        line = self.env["account.move.line"].create(
            {
                "display_type": "line_note",
                "name": __name__,
                "move_id": self.invoice.id,
            }
        )
        self.assertEqual(line.move_name, "TEST")
        self.invoice.name = "TEST2"
        self.assertEqual(line.move_name, "TEST2")

    def test_in_invoice_create_refund(self):
        """Test creating a refund from a vendor bill.

        If auditlog does not carefully separate the main transaction cache from
        the cache that it uses to fetch the logged values, this test would fail
        on the loss of values related to the dynamic syncing of invoice and
        journal entry lines.
        """
        self.invoice.action_post()

        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=self.invoice.ids)
            .create(
                {
                    "date": fields.Date.from_string("2019-02-01"),
                    "reason": "no reason",
                    "journal_id": self.invoice.journal_id.id,
                }
            )
        )
        move_reversal.refund_moves()
