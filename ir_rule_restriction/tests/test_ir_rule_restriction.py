# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
from odoo.osv.expression import TRUE_LEAF, FALSE_LEAF


class TestIrRuleRestrictions(TransactionCase):

    post_install = True
    at_install = False

    def test_ir_rule_restrictions(self):
        """ The test goes as follows:
        1) create userA, groupA and have the userA be a member of groupA
        2) Verify that userA can read res.partners
        3) Add ruleA and ruleB, both with FALSE_LEAF, verify that the user can
        still read
        4) Make ruleA.and_rule = True and verify that user cannot read the
        record now.
        """
        model_res_partner = self.env['res.partner']
        model_ir_rule = self.env['ir.rule']
        ir_model_res_partner = self.env['ir.model'].search([
            ('model', '=', 'res.partner')])
        userA = self.env['res.users'].create({
            'name': 'userA',
            'login': 'userA',
        })
        model_res_partner = model_res_partner.sudo(userA.id)
        groupA = self.env['res.groups'].create({'name': 'groupA'})
        groupA.write({'users': [(6, 0, userA.ids)]})
        self.assertNotEquals(model_res_partner.search_count([]), 0L)
        # global rule, permissive
        model_ir_rule.create({
            'name': 'ruleA',
            'domain_force': [TRUE_LEAF],
            'model_id': ir_model_res_partner.id,
        })
        self.assertNotEquals(model_res_partner.search_count([]), 0L)
        # group rule, normally can only add permissions, here restricts
        model_ir_rule.create({
            'name': 'ruleB',
            'domain_force': [FALSE_LEAF],
            'model_id': ir_model_res_partner.id,
            'and_rule': True,
            'groups': [(6, 0, groupA.ids)],
        })
        self.assertEquals(model_res_partner.search_count([]), 0L)
