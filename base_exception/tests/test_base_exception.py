# -*- coding: utf-8 -*-
# © 2016 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common

import logging

_logger = logging.getLogger(__name__)


# @common.at_install(False)
# @common.post_install(True)
class TestBaseException(common.TransactionCase):

    def setUp(self):
        super(TestBaseException, self).setUp()

        self.base_exception = self.env['base.exception']
        self.exception_rule = self.env['exception.rule']
        self.exception_confirm = self.env['exception.rule.confirm']

        self.exception_rule._fields['rule_group'].selection.append(
            ('test_base', 'test base exception')
        )
        self.exception_rule._fields['model'].selection.append(
            ('base.exception.test.purchase',
             'base.exception.test.purchase')
        )
        self.exception_rule._fields['model'].selection.append(
            ('base.exception.test.purchase.line',
             'base.exception.test.purchase.line')
        )
        self.exceptionnozip = self.env['exception.rule'].create({
            'name': "No ZIP code on destination",
            'sequence': 10,
            'rule_group': "test_base",
            'model': "base.exception.test.purchase",
            'code': """if not test_base.partner_id.zip:
    failed=True""",
        })
        self.exceptionno_minorder = self.env['exception.rule'].create({
            'name': "Min order except",
            'sequence': 10,
            'rule_group': "test_base",
            'model': "base.exception.test.purchase",
            'code': """if test_base.amount_total <= 200.0:
    failed=True""",
        })

        self.exceptionno_lineqty = self.env['exception.rule'].create({
            'name': "Qty > 0",
            'sequence': 10,
            'rule_group': "test_base",
            'model': "base.exception.test.purchase.line",
            'code': """if test_base_line.qty <= 0:
        failed=True"""})

    def test_sale_order_exception(self):
        partner = self.env.ref('base.res_partner_1')
        partner.zip = False
        potest1 = self.env['base.exception.test.purchase'].create({
            'name': 'Test base exception to basic purchase',
            'partner_id': partner.id,
            'line_ids': [(0, 0, {'name': "line test",
                                 'amount': 120.0,
                                 'qty': 1.5})],
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
