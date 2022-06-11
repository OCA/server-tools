# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestBaseExternalExemple(TransactionCase):

    def test_sale_order_crud(self):

        external_order_obj = self.env['external.sale.order']

        customer = self.env.ref('base.main_partner')
        product = self.env.ref('product.product_product_5_product_template')

        external_order = external_order_obj.create({
            'partner_id': customer.id,
            'date_order': "2022-06-30 00:00:00",
            'origin': "My origin",
            'order_line': [(0, 0, {
                "product_id": product.id,
                "name": "My product",
                "product_uom_qty": 1,
                "unit_price": 50,
            })]
        })

        self.assertEqual(external_order.partner_id.id, customer.id)
        self.assertEqual(external_order.date_order, "2022-06-30 00:00:00")
