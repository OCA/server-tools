# Copyright 2016 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import ValidationError
from odoo import fields
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
        if 'test_purchase_ids' not in cls.exception_rule._fields:
            field = fields.Many2many('base.exception.test.purchase')
            cls.exception_rule._add_field('test_purchase_ids', field)
        cls.exception_confirm = cls.env['exception.rule.confirm']
        cls.exception_rule._fields['model'].selection.append(
            ('base.exception.test.purchase', 'Purchase Order'))

        cls.exception_rule._fields['model'].selection.append(
            ('base.exception.test.purchase.line', 'Purchase Order Line'))

        cls.exceptionnozip = cls.env['exception.rule'].create({
            'name': "No ZIP code on destination",
            'sequence': 10,
            'model': "base.exception.test.purchase",
            'code': "if not obj.partner_id.zip: failed=True",
        })

        cls.exceptionno_minorder = cls.env['exception.rule'].create({
            'name': "Min order except",
            'sequence': 10,
            'model': "base.exception.test.purchase",
            'code': "if obj.amount_total <= 200.0: failed=True",
        })

        cls.exceptionno_lineqty = cls.env['exception.rule'].create({
            'name': "Qty > 0",
            'sequence': 10,
            'model': "base.exception.test.purchase.line",
            'code': "if obj.qty <= 0: failed=True"
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
        # Block because of exception during validation
        with self.assertRaises(ValidationError):
            potest1.button_confirm()
        # Test that we have linked exceptions
        self.assertTrue(potest1.exception_ids)
        # Test ignore exeception make possible for the po to validate
        potest1.ignore_exception = True
        potest1.button_confirm()
        self.assertTrue(potest1.state == 'purchase')
