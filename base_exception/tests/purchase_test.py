# Copyright 2016 Akretion Mourad EL HADJ MIMOUNE
# Copyright 2020 Hibou Corp.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"
    _name = "exception.rule"

    method = fields.Selection(
        selection_add=[("exception_method_no_zip", "Purchase exception no zip")]
    )
    model = fields.Selection(
        selection_add=[("base.exception.test.purchase", "Purchase Test")],
        ondelete={"base.exception.test.purchase": "cascade"},
    )
    test_purchase_ids = fields.Many2many("base.exception.test.purchase")


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
    amount_total = fields.Float(compute="_compute_amount_total", store=True)

    @api.depends("line_ids")
    def _compute_amount_total(self):
        for record in self:
            for line in record.line_ids:
                record.amount_total += line.amount * line.qty

    @api.constrains("ignore_exception", "line_ids", "state")
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

    def _reverse_field(self):
        return "test_purchase_ids"

    def exception_method_no_zip(self):
        records_fail = self.env["base.exception.test.purchase"]
        for rec in self:
            if not rec.partner_id.zip:
                records_fail += rec
        return records_fail


class LineTest(models.Model):
    _name = "base.exception.test.purchase.line"
    _description = "Base Exception Test Model Line"

    name = fields.Char()
    lead_id = fields.Many2one("base.exception.test.purchase", ondelete="cascade")
    qty = fields.Float()
    amount = fields.Float()
