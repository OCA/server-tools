# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields
from odoo.addons.web_external_odoo.models.models import ExternalOdooClient

# import logging
# _logger = logging.getLogger()


# Comment if (_.IsNumber(resId)) { in addons/web/static/js/views/basic/basic_model.js
# in _readUngroupedList to avoid problem with our UUIDs

odoo_client = ExternalOdooClient(
    url="http://localhost:8069",
    db="test",
    username="admin",
    password="admin",
)


class ExternalSaleOrder(models.Model):

    _name = 'external.sale.order'

    _inherit = ['web_external.model']

    _external_client = odoo_client
    _external_name = "sale.order"

    name = fields.Char(
        "Number", readonly=True,
        external=True, external_name="name")
    partner_id = fields.Many2one(
        'res.partner', "Partner",
        required=True,
        external=True, external_name="partner_id")
    date_order = fields.Datetime(
        required=True,
        external=True, external_name="date_order")
    origin = fields.Char(
        external=True, external_name="origin")
    order_line = fields.One2many(
        'external.sale.order.line', 'order_id',
        'Lines',
        external=True, external_name="order_line")
    amount_untaxed = fields.Float(
        "Untaxed amount", readonly=True,
        external=True, external_name="amount_untaxed")
    amount_tax = fields.Float(
        "Taxes", readonly=True,
        external=True, external_name="amount_tax")
    amount_total = fields.Float(
        "Total", readonly=True,
        external=True, external_name="amount_total")
    state = fields.Char(
        "State", readonly=True,
        external=True, external_name="state")


class ExternalSaleOrderLine(models.Model):

    _name = 'external.sale.order.line'

    _inherit = ['web_external.model']

    _external_client = odoo_client
    _external_name = "sale.order.line"

    order_id = fields.Many2one(
        "external.sale.order", required=True,
        external=True, external_name="order_id")
    product_id = fields.Many2one(
        "product.product", "Product", required=True,
        external=True, external_name="product_id")
    name = fields.Char(
        "Description", required=True,
        external=True, external_name="name")
    product_uom_qty = fields.Float(
        "Quantity", required=True,
        external=True, external_name="product_uom_qty")
    price_unit = fields.Float(
        "Unit price", required=True,
        external=True, external_name="price_unit")
    tax_id = fields.Many2many(
        comodel_name='account.tax', string='Taxes',
        external=True, external_name="tax_id")
    price_subtotal = fields.Float(
        "Subtotal", readonly=True,
        external=True, external_name="price_subtotal")
