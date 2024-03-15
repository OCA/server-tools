# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import exceptions
from odoo.tests.common import SavepointCase


class TestInvoiceAttachmentOwnerRule(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestInvoiceAttachmentOwnerRule, cls).setUpClass()

        cls.user1 = cls.env.ref("base.user_admin")
        cls.user2 = cls.user1.copy(
            {
                "name": "user2",
                "login": "test2",
                "groups_id": [(6, 0, cls.env.ref("base.group_user").ids)],
            }
        )
        cls.user3_admin = cls.env["res.users"].create(
            {
                "name": "User admin",
                "login": "test admin",
                "groups_id": [(6, 0, cls.env.ref("base.group_system").ids)],
            }
        )

        cls.product = cls.env.ref("product.product_product_4")

        cls.so = (
            cls.env["sale.order"]
            .with_user(cls.user1)
            .create(
                {
                    "partner_id": cls.user2.partner_id.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": "sol1",
                                "product_id": cls.product.id,
                                "product_uom_qty": 2,
                                "product_uom": cls.product.uom_id.id,
                                "price_unit": 100.00,
                            },
                        )
                    ],
                }
            )
        )

        cls.so.order_line.write({"qty_delivered": cls.so.order_line.product_uom_qty})
        cls.so.action_confirm()
        cls.so._create_invoices()
        cls.invoice = cls.so.invoice_ids

    def test_1_owner_can_delete_attachment(self):
        attachment_sale = (
            self.env["ir.attachment"]
            .with_user(self.user1)
            .create(
                {
                    "name": "PJ test",
                    "res_model": "sale.order",
                    "res_id": self.so.id,
                    "datas": base64.b64encode(b"\xff data"),
                }
            )
        )
        self.assertTrue(
            self.env["ir.attachment"].search(
                [("res_model", "=", "sale.order"), ("name", "=", "PJ test")], limit=1
            )
        )
        with self.assertRaises(exceptions.UserError):
            attachment_sale.with_user(self.user2).unlink()

        attachment_sale.with_user(self.user1).unlink()

        self.assertFalse(
            self.env["ir.attachment"].search(
                [("res_model", "=", "sale.order"), ("name", "=", "PJ test")], limit=1
            )
        )

    def test_2_root_and_admin_can_delete_attachment(self):
        attachment_invoice = (
            self.env["ir.attachment"]
            .with_user(self.user1)
            .create(
                {
                    "name": "PJ test 2",
                    "res_model": "account.invoice",
                    "res_id": self.invoice.id,
                    "datas": base64.b64encode(b"\xff data"),
                }
            )
        )

        attachment_invoice.with_user(self.user3_admin).unlink()
        self.assertFalse(
            self.env["ir.attachment"].search(
                [("res_model", "=", "account_invoice"), ("name", "=", "PJ test 2")],
                limit=1,
            )
        )
