# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RequestProductLine(models.Model):
    _name = "request.product.line"
    _description = "Product Line"

    _check_company_auto = True

    request_id = fields.Many2one("request.request", required=True)
    description = fields.Char("Description", required=True)
    company_id = fields.Many2one(
        string="Company",
        related="request_id.company_id",
        store=True,
        readonly=True,
        index=True,
    )
    product_id = fields.Many2one(
        "product.product", string="Products", check_company=True
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    quantity = fields.Float("Quantity", default=1.0)
    price_unit = fields.Float("Unit Price", default=1.0)
    price_subtotal = fields.Float(
        "Total", default=1.0, compute="_compute_price_subtotal"
    )
    resource_ref = fields.Reference(
        string="Line Ref",
        selection=lambda self: [
            (model.model, model.name) for model in self.env["ir.model"].search([])
        ],
        readonly=True,
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
            if not self.description:
                self.description = self.product_id.display_name
        else:
            self.product_uom_id = None

    @api.depends("quantity", "price_unit")
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.quantity
