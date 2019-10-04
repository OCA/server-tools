# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import ValidationError


@common.at_install(False)
@common.post_install(True)
class TestSaleOrderLineMinQty(common.TransactionCase):
    def setUp(self):
        super(TestSaleOrderLineMinQty, self).setUp()

        # Create models
        self.sale_order_model = self.env["sale.order"]
        self.sale_order_line_model = self.env["sale.order.line"]
        self.partner_model = self.env["res.partner"]
        self.product_model = self.env["product.product"]
        self.sale_order = self.sale_order_model
        # Create partner and product
        self.partner = self.partner_model.create({"name": "Test partner"})
        self.product = self.product_model.create(
            {
                "name": "Test product",
                "sale_min_qty": 10.0,
                "force_sale_min_qty": False,
            }
        )

    def test_check_sale_order_min_qty_required(self):
        line_values = {"product_id": self.product.id, "product_uom_qty": 5.0}
        # Create sale order line with Qty less than min Qty
        with self.assertRaises(ValidationError):
            self.sale_order = self.sale_order_model.create(
                {
                    "partner_id": self.partner.id,
                    "order_line": [(0, 0, line_values)],
                }
            )
        line_values["product_uom_qty"] = 12.0
        # Create sale order line with Qty great then min Qty
        self.sale_order = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "order_line": [(0, 0, line_values)],
            }
        )
        self.assertFalse(self.sale_order.order_line.is_qty_less_min_qty)

        self.assertEqual(self.sale_order.order_line.product_uom_qty, 12.0)

    def test_check_sale_order_min_qty_recommended(self):
        line_values = {"product_id": self.product.id, "product_uom_qty": 5.0}
        # Set Force min Qty to true
        self.product.force_sale_min_qty = True

        # Create sale order line with Qty less than min Qty
        self.sale_order = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "order_line": [(0, 0, line_values)],
            }
        )
        self.assertTrue(self.sale_order.order_line.is_qty_less_min_qty)

        self.assertEqual(self.sale_order.order_line.product_uom_qty, 5.0)
