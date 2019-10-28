# Copyright 2019 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo import api
from .common import setup_test_model
from .sale_test import SaleTest, LineTest


class TestBaseSubstate(TransactionCase):

    def setUp(self):
        super(TestBaseSubstate, self).setUp()

        self.registry.enter_test_mode(self.cr)
        self.old_cursor = self.cr
        self.cr = self.registry.cursor()
        self.env = api.Environment(self.cr, self.uid, {})
        setup_test_model(self.env, [SaleTest, LineTest])
        # self.substate_test_sale = self._init_test_model(SaleTest)
        # self.substate_test_sale_line = self._init_test_model(LineTest)
        self.substate_test_sale = self.env['base.substate.test.sale']
        self.substate_test_sale_line = self.env['base.substate.test.sale.line']

        self.base_substate = self.env['base.substate.mixin']
        self.substate_type = self.env['base.substate.type']

        self.substate_type._fields['model'].selection.append(
            ('base.substate.test.sale', 'Sale Order'))

        self.substate_type = self.env['base.substate.type'].create({
            'name': "Sale",
            'model': "base.substate.test.sale",
            'target_state_field': "state",
        })

        self.substate_val_quotation = self.env['target.state.value'].create({
            'name': "Quotation",
            'base_substate_type_id': self.substate_type.id,
            'target_state_value': "draft",
        })

        self.substate_val_sale = self.env['target.state.value'].create({
            'name': "Sale order",
            'base_substate_type_id': self.substate_type.id,
            'target_state_value': "sale",
        })
        self.substate_under_negotiation = self.env['base.substate'].create({
            'name': "Under negotiation",
            'sequence': 1,
            'target_state_value_id': self.substate_val_quotation.id,
        })

        self.substate_won = self.env['base.substate'].create({
            'name': "Won",
            'sequence': 1,
            'target_state_value_id': self.substate_val_quotation.id,
        })

        self.substate_wait_docs = self.env['base.substate'].create({
            'name': "Waiting for legal documents",
            'sequence': 2,
            'target_state_value_id': self.substate_val_sale.id,
        })

        self.substate_valid_docs = self.env['base.substate'].create({
            'name': "To validate legal documents",
            'sequence': 3,
            'target_state_value_id': self.substate_val_sale.id,
        })

        self.substate_in_delivering = self.env['base.substate'].create({
            'name': "In delivering",
            'sequence': 4,
            'target_state_value_id': self.substate_val_sale.id,
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
