# -*- coding: utf-8 -*-
# © 2017 innoviù Srl <http://www.innoviu.com>
# © 2017 Agile Business Group Sagl <http://www.agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestIrRule(TransactionCase):

    def setUp(self):
        super(TestIrRule, self).setUp()

        # Create new Company and link demo user to it
        self.company_model = self.env['res.company']
        self.partner_model = self.env['res.partner']
        self.user_model = self.env['res.users']

        self.company1 = self.company_model.create({
            'name': 'company1'
        })
        self.partner1 = self.partner_model.create({
            'name': 'partner1',
            'company_id': self.company1.id
        })
        self.user1 = self.user_model.create({
            'name': 'user1',
            'login': 'user1',
            'partner_id': self.partner1.id,
            'company_id': self.company1.id,
            'company_ids': [self.company1.id]
        })

        self.company2 = self.company_model.create({
            'name': 'company2'
        })

    def test_bypass_ir_rule(self):
        # User1 can only see his own company
        self.assertEqual(
            self.company_model.sudo(self.user1.id).search_count([]), 1
        )

        # Add the context
        ctx = {'can_bypass_record_rules': ['base.group_user']}

        # User1 can still only see his own company
        self.assertEqual(
            self.company_model.sudo(self.user1.id).search_count([]), 1
        )

        # Check the flag in every rule regarding company model
        ir_rule_model = self.env['ir.rule']
        rules_on_company = ir_rule_model.search([
            ('model_id', '=', 'res.company')
        ])
        for rule in rules_on_company:
            rule.sudo().update({
                'can_be_bypassed': True
            })

        # Now User1 can see every company
        self.assertGreater(
            self.company_model.sudo(self.user1.id)
                .with_context(ctx).search_count([]), 1
        )
