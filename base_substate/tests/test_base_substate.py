# Copyright 2019 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tests import common
from .common import setup_test_model


@common.at_install(False)
@common.post_install(True)
class TestBaseSubstate(common.SavepointCase):
    class SaleTest(models.Model):
        _inherit = 'base.substate.mixin'
        _name = "base.substate.test.sale"
        _description = "Base substate Test Model"

        name = fields.Char(required=True)
        user_id = fields.Many2one('res.users', string='Responsible')
        state = fields.Selection(
            [('draft', 'New'), ('cancel', 'Cancelled'),
             ('sale', 'Sale'),
             ('done', 'Done')],
            string="Status", readonly=True, default='draft')
        active = fields.Boolean(default=True)
        partner_id = fields.Many2one('res.partner', string='Partner')
        line_ids = fields.One2many(
            'base.substate.test.sale.line', 'sale_id')
        amount_total = fields.Float(
            compute='_compute_amount_total', store=True)

        @api.depends('line_ids')
        def _compute_amount_total(cls):
            for record in cls:
                for line in record.line_ids:
                    record.amount_total += line.amount * line.qty

        @api.multi
        def button_confirm(cls):
            cls.write({'state': 'sale'})
            return True

        @api.multi
        def button_cancel(cls):
            cls.write({'state': 'cancel'})


    class LineTest(models.Model):
        _name = "base.substate.test.sale.line"
        _description = "Base substate Test Model Line"

        name = fields.Char()
        sale_id = fields.Many2one('base.substate.test.sale',
                                  ondelete='cascade')
        qty = fields.Float()
        amount = fields.Float()


    @classmethod
    def setUpClass(cls):
        super(TestBaseSubstate, cls).setUpClass()
        # from .sale_test import SaleTest, LineTest

        setup_test_model(cls.env, [cls.SaleTest, cls.LineTest])

        cls.substate_test_sale = cls.env['base.substate.test.sale']
        cls.substate_test_sale_line = cls.env['base.substate.test.sale.line']

        cls.base_substate = cls.env['base.substate.mixin']
        cls.substate_type = cls.env['base.substate.type']

        cls.substate_type._fields['model'].selection.append(
            ('base.substate.test.sale', 'Sale Order'))

        cls.substate_type = cls.env['base.substate.type'].create({
            'name': "Sale",
            'model': "base.substate.test.sale",
            'target_state_field': "state",
        })

        cls.substate_val_quotation = cls.env['target.state.value'].create({
            'name': "Quotation",
            'base_substate_type_id': cls.substate_type.id,
            'target_state_value': "draft",
        })

        cls.substate_val_sale = cls.env['target.state.value'].create({
            'name': "Sale order",
            'base_substate_type_id': cls.substate_type.id,
            'target_state_value': "sale",
        })
        cls.substate_under_negotiation = cls.env['base.substate'].create({
            'name': "Under negotiation",
            'sequence': 1,
            'target_state_value_id': cls.substate_val_quotation.id,
        })

        cls.substate_won = cls.env['base.substate'].create({
            'name': "Won",
            'sequence': 1,
            'target_state_value_id': cls.substate_val_quotation.id,
        })

        cls.substate_wait_docs = cls.env['base.substate'].create({
            'name': "Waiting for legal documents",
            'sequence': 2,
            'target_state_value_id': cls.substate_val_sale.id,
        })

        cls.substate_valid_docs = cls.env['base.substate'].create({
            'name': "To validate legal documents",
            'sequence': 3,
            'target_state_value_id': cls.substate_val_sale.id,
        })

        cls.substate_in_delivering = cls.env['base.substate'].create({
            'name': "In delivering",
            'sequence': 4,
            'target_state_value_id': cls.substate_val_sale.id,
        })

    def test_sale_order_substate(self):
        partner = self.env.ref('base.res_partner_1')
        so_test1 = self.substate_test_sale.create({
            'name': 'Test base substate to basic sale',
            'partner_id': partner.id,
            'line_ids': [(0, 0, {
                'name': "line test",
                'amount': 120.0,
                'qty': 1.5,
            })],
        })
        self.assertTrue(so_test1.state == 'draft')
        self.assertTrue(so_test1.substate_id ==
                        self.substate_under_negotiation)

        # Test that validation of sale order change substate_id
        so_test1.button_confirm()
        self.assertTrue(so_test1.state == 'sale')
        self.assertTrue(so_test1.substate_id == self.substate_wait_docs)

        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        so_test1.button_cancel()
        self.assertTrue(so_test1.state == 'cancel')
        self.assertTrue(not so_test1.substate_id)
