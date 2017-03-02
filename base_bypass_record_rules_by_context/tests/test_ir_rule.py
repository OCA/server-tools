# -*- coding: utf-8 -*-
# © 2017 innoviù Srl <http://www.innoviu.com>
# © 2017 Agile Business Group Sagl <http://www.agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestIrRule(TransactionCase):

    def setUp(self):
        super(TestIrRule, self).setUp()

        # Create new Company and link demo user to it
        self.company_obj = self.env['res.company']
        self.partner_obj = self.env['res.partner']

        self.admin_user = self.env.ref('base.user_root')
        self.new_company_partner = self.admin_user.company_id.partner_id.copy({
            'name': 'Company 2'
        })
        self.new_company = self.admin_user.company_id.copy({
            'name': 'Company 2',
            'partner_id': self.new_company_partner.id
        })

        self.demo_user = self.env.ref('base.user_demo')
        self.demo_user.write(
            {
                'company_id': self.new_company.id
            }
        )

    def test_bypass_ir_rule_by_ctx(self):
        # Only demo partner belongs to Company 2
        self.assertTrue(
            len(self.partner_obj.sudo(self.demo_user.id).search([])) == 1
        )
        # By pass rule by context
        ctx = {'bypass_record_rules': True}
        self.assertTrue(
            len(self.partner_obj.sudo(
                self.demo_user.id).with_context(ctx).search([])) > 1
        )
