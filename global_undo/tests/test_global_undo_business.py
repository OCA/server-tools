# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Business actions and the accounting rules that outrank the undo history.

Skipped when the modules they target are not installed: the hooks are optional
by design, and the module must stay usable on a bare database.
"""

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGlobalUndoBusiness(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Transaction = cls.env["global.undo.transaction"]
        cls.Operation = cls.env["global.undo.operation"]
        # An administrator: confirming orders and posting entries needs the
        # rights of one, and the journal records their work like anyone else's.
        cls.uenv = cls.env(user=cls.env.ref("base.user_admin"))

    def step(self):
        self.env.cr.gu_transaction_id = False

    def undo(self):
        return self.Transaction.with_env(self.uenv).gu_apply_next("undo")

    def redo(self):
        return self.Transaction.with_env(self.uenv).gu_apply_next("redo")

    def _require_accounting(self):
        if "account.account" not in self.env or not self.uenv["account.account"].search(
            [], limit=1
        ):
            self.skipTest("no chart of accounts installed")

    def _partner(self):
        return self.uenv["res.partner"].create({"name": "GU Business Partner"})

    def test_sale_confirmation_is_a_single_undoable_step(self):
        if "sale.order" not in self.env:
            self.skipTest("sale is not installed")
        self.assertTrue(
            getattr(
                self.env.registry["sale.order"].action_confirm, "_gu_patched", False
            ),
            "the business action hook was not registered",
        )
        product = self.uenv["product.product"].create(
            {
                "name": "GU Service",
                "type": "service",
                "list_price": 100,
            }
        )
        order = self.uenv["sale.order"].create(
            {
                "partner_id": self._partner().id,
                "order_line": [
                    (0, 0, {"product_id": product.id, "product_uom_qty": 2})
                ],
            }
        )
        self.step()
        order.action_confirm()
        self.assertEqual(order.state, "sale")

        operation = self.Operation.with_env(self.uenv).search(
            [("kind", "=", "action"), ("model_name", "=", "sale.order")], limit=1
        )
        self.assertEqual(operation.method, "action_confirm")

        result = self.undo()
        self.assertTrue(result["done"], result["message"])
        order.invalidate_recordset()
        self.assertEqual(order.state, "draft")

        result = self.redo()
        self.assertTrue(result["done"], result["message"])
        order.invalidate_recordset()
        self.assertEqual(order.state, "sale")

    def _invoice(self, price):
        return self.uenv["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self._partner().id,
                "invoice_line_ids": [
                    (0, 0, {"name": "GU line", "quantity": 1, "price_unit": price})
                ],
            }
        )

    def test_posting_an_entry_can_be_undone(self):
        self._require_accounting()
        invoice = self._invoice(50)
        self.step()
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

        result = self.undo()
        self.assertTrue(result["done"], result["message"])
        invoice.invalidate_recordset()
        self.assertEqual(invoice.state, "draft")

    def test_a_posted_entry_refuses_a_plain_write_undo(self):
        self._require_accounting()
        invoice = self._invoice(50)
        invoice.action_post()
        self.step()
        invoice.write({"ref": "GU ref"})

        operation = self.Operation.with_env(self.uenv).search(
            [
                ("kind", "=", "write"),
                ("model_name", "=", "account.move"),
                ("res_id", "=", invoice.id),
            ],
            limit=1,
        )
        self.assertTrue(operation)
        self.assertIn("posted", operation._gu_blocker("undo") or "")

    def test_ledger_rows_are_never_journalled(self):
        self._require_accounting()
        self._invoice(50).action_post()
        self.assertFalse(
            self.Operation.with_env(self.uenv).search_count(
                [("model_name", "=", "account.move.line")]
            ),
            "ledger rows leaked into the journal",
        )

    def test_a_paid_invoice_cannot_be_unposted(self):
        self._require_accounting()
        invoice = self._invoice(70)
        self.step()
        invoice.action_post()
        operation = self.Operation.with_env(self.uenv).search(
            [
                ("kind", "=", "action"),
                ("model_name", "=", "account.move"),
                ("res_id", "=", invoice.id),
            ],
            limit=1,
        )

        self.uenv["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=invoice.ids,
        ).create({}).action_create_payments()
        invoice.invalidate_recordset()

        self.assertNotEqual(invoice.payment_state, "not_paid")
        self.assertIn("reconciled", operation._gu_blocker("undo") or "")
