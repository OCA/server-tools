# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
import os
from odoo import api, fields, models, tools
import logging

_logger = logging.getLogger(__name__)

testing = tools.config.get('test_enable') or os.environ.get('ODOO_TEST_ENABLE')
if testing:
    class PurchaseTest(models.Model):
        _inherit = 'base.exception'
        _name = "base.exception.test.purchase"
        _description = "Base Ecxeption Test Model"

        rule_group = fields.Selection(
            selection_add=[('test_base', 'test')],
            default='test_base',
        )
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
        def _compute_amount_total(self):
            for record in self:
                for line in record.line_ids:
                    record.amount_total += line.amount * line.qty

        @api.constrains('ignore_exception', 'line_ids', 'state')
        def test_purchase_check_exception(self):
            orders = self.filtered(lambda s: s.state == 'purchase')
            if orders:
                orders._check_exception()

        @api.multi
        def button_approve(self, force=False):
            self.write({'state': 'to approve'})
            return {}

        @api.multi
        def button_draft(self):
            self.write({'state': 'draft'})
            return {}

        @api.multi
        def button_confirm(self):
            self.write({'state': 'purchase'})
            return True

        @api.multi
        def button_cancel(self):
            self.write({'state': 'cancel'})

        def test_base_get_lines(self):
            self.ensure_one()
            return self.line_ids

    class LineTest(models.Model):
        _name = "base.exception.test.purchase.line"
        _description = "Base Ecxeption Test Model Line"

        name = fields.Char()
        lead_id = fields.Many2one('base.exception.test.purchase',
                                  ondelete='cascade')
        qty = fields.Float()
        amount = fields.Float()
