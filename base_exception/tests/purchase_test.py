# Copyright 2016 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class PurchaseTest(models.Model):
    _inherit = 'base.exception'
    _name = "base.exception.test.purchase"
    _description = "Base Ecxeption Test Model"

    name = fields.Char(required=True)
    user_id = fields.Many2one('res.users', string='Responsible')
    state = fields.Selection(
        [('draft', 'New'), ('cancel', 'Cancelled'),
         ('purchase', 'Purchase'),
         ('to approve', 'To approve'), ('done', 'Done')],
        string="Status", readonly=True, default='draft')
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    line_ids = fields.One2many(
        'base.exception.test.purchase.line', 'lead_id')
    amount_total = fields.Float(
        compute='_compute_amount_total', store=True)

    @api.depends('line_ids')
    def _compute_amount_total(cls):
        for record in cls:
            for line in record.line_ids:
                record.amount_total += line.amount * line.qty

    @api.constrains('ignore_exception', 'line_ids', 'state')
    def test_purchase_check_exception(cls):
        orders = cls.filtered(lambda s: s.state == 'purchase')
        if orders:
            orders._check_exception()

    @api.multi
    def button_approve(cls, force=False):
        cls.write({'state': 'to approve'})
        return {}

    @api.multi
    def button_draft(cls):
        cls.write({'state': 'draft'})
        return {}

    @api.multi
    def button_confirm(cls):
        cls.write({'state': 'purchase'})
        return True

    @api.multi
    def button_cancel(cls):
        cls.write({'state': 'cancel'})

    @api.multi
    def _reverse_field(self):
        return 'test_purchase_ids'


class LineTest(models.Model):
    _name = "base.exception.test.purchase.line"
    _description = "Base Exception Test Model Line"

    name = fields.Char()
    lead_id = fields.Many2one('base.exception.test.purchase',
                              ondelete='cascade')
    qty = fields.Float()
    amount = fields.Float()
