# Copyright 2016 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from .common import setup_test_model
from .purchase_test import PurchaseTest, LineTest
import logging

_logger = logging.getLogger(__name__)


@common.at_install(False)
@common.post_install(True)
class TestBaseException(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestBaseException, cls).setUpClass()
        setup_test_model(cls.env, [PurchaseTest, LineTest])

        cls.base_exception = cls.env['base.exception']
        cls.exception_rule = cls.env['exception.rule']
        cls.exception_confirm = cls.env['exception.rule.confirm']

        cls.exception_rule._fields['rule_group'].selection.append(
            ('test_base', 'Test Base Exception'))

        cls.exception_rule._fields['model'].selection.append(
            ('base.exception.test.purchase', 'Purchase Order'))

        cls.exception_rule._fields['model'].selection.append(
            ('base.exception.test.purchase.line', 'Purchase Order Line'))

        cls.exceptionnozip = cls.env['exception.rule'].create({
            'name': "No ZIP code on destination",
            'sequence': 10,
            'rule_group': "test_base",
            'model': "base.exception.test.purchase",
            'code': "if not test_base.partner_id.zip: failed=True",
        })

        cls.exceptionno_minorder = cls.env['exception.rule'].create({
            'name': "Min order except",
            'sequence': 10,
            'rule_group': "test_base",
            'model': "base.exception.test.purchase",
            'code': "if test_base.amount_total <= 200.0: failed=True",
        })

        cls.exceptionno_lineqty = cls.env['exception.rule'].create({
            'name': "Qty > 0",
            'sequence': 10,
            'rule_group': "test_base",
            'model': "base.exception.test.purchase.line",
            'code': "if test_base_line.qty <= 0: failed=True"
        })

    def test_purchase_order_exception(self):
        partner = self.env.ref('base.res_partner_1')
        partner.zip = False
        potest1 = self.env['base.exception.test.purchase'].create({
            'name': 'Test base exception to basic purchase',
            'partner_id': partner.id,
            'line_ids': [(0, 0, {
                'name': "line test",
                'amount': 120.0,
                'qty': 1.5,
            })],
        })

        potest1.button_confirm()
        # Set ignore_exception flag  (Done after ignore is selected at wizard)
        potest1.ignore_exception = True
        potest1.button_confirm()
        self.assertTrue(potest1.state == 'purchase')
        # Simulation the opening of the wizard exception_confirm and
        # set ignore_exception to True
        except_confirm = self.exception_confirm.with_context(
            {
                'active_id': potest1.id,
                'active_ids': [potest1.id],
                'active_model': potest1._name
            }).new({'ignore': True})
        except_confirm.action_confirm()
        self.assertTrue(potest1.ignore_exception)
