# Copyright 2016 Akretion Mourad EL HADJ MIMOUNE
# Copyright 2020 Hibou Corp.
# Copyright 2025 Raumschmiede GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"
    _name = "exception.rule"

    method = fields.Selection(
        selection_add=[("exception_method_no_zip", "Purchase exception no zip")]
    )
    model = fields.Selection(
        selection_add=[
            ("base.exception.test.purchase", "Purchase Test"),
            ("base.exception.test.purchase.line", "Purchase Test Line"),
            ("base.exception.method.test.purchase.line", "Purchase Test Method Line"),
        ],
        ondelete={
            "base.exception.test.purchase": "cascade",
            "base.exception.test.purchase.line": "cascade",
            "base.exception.method.test.purchase.line": "cascade",
        },
    )


class PurchaseTest(models.Model):
    _inherit = "base.exception"
    _name = "base.exception.test.purchase"
    _description = "Base Exception Test Model"

    name = fields.Char(required=True)
    user_id = fields.Many2one("res.users", string="Responsible")
    state = fields.Selection(
        [
            ("draft", "New"),
            ("cancel", "Cancelled"),
            ("purchase", "Purchase"),
            ("to approve", "To approve"),
            ("done", "Done"),
        ],
        string="Status",
        readonly=True,
        default="draft",
    )
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    line_ids = fields.One2many("base.exception.test.purchase.line", "lead_id")
    line_method_ids = fields.One2many(
        "base.exception.method.test.purchase.line", "lead_id"
    )
    amount_total = fields.Float(compute="_compute_amount_total", store=True)

    @api.depends("line_ids")
    def _compute_amount_total(self):
        for record in self:
            for line in record.line_ids:
                record.amount_total += line.amount * line.qty

    @api.constrains("ignore_exception", "line_ids", "line_method_ids", "state")
    def test_purchase_check_exception(self):
        orders = self.filtered(lambda s: s.state == "purchase")
        if orders:
            orders._check_exception()

    def button_approve(self, force=False):
        self.write({"state": "to approve"})
        return {}

    def button_draft(self):
        self.write({"state": "draft"})
        return {}

    def button_confirm(self):
        self.write({"state": "purchase"})
        return True

    def button_cancel(self):
        self.write({"state": "cancel"})

    def _get_sub_exception_field_names(self):
        return ["line_ids", "line_method_ids"]

    def exception_method_no_zip(self):
        records_fail = self.env["base.exception.test.purchase"]
        for rec in self:
            if not rec.partner_id.zip:
                records_fail += rec
        return records_fail


class LineTest(models.Model):
    _inherit = "base.exception"
    _name = "base.exception.test.purchase.line"
    _description = "Base Exception Test Model Line"

    name = fields.Char()
    lead_id = fields.Many2one("base.exception.test.purchase", ondelete="cascade")
    qty = fields.Float()
    amount = fields.Float()

    def _get_main_records(self):
        return self.lead_id


class LineTestMethod(models.Model):
    _inherit = "base.exception.method"
    _name = "base.exception.method.test.purchase.line"
    _description = "Base Exception Test Model Line"

    name = fields.Char()
    lead_id = fields.Many2one("base.exception.test.purchase", ondelete="cascade")
    qty = fields.Float()
    amount = fields.Float()

    # Models inheriting from .method must implement this field as their records
    # are filtered based on this field
    ignore_exception = fields.Boolean("Ignore Exceptions", copy=False)

    # This model here must override _get_main_records as it has no exception_ids
    def _get_main_records(self):
        return self.lead_id
