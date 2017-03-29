# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestBaseDomainOperator(TransactionCase):
    def test_base_domain_operator(self):
        self.env['base.domain.operator']._register_hook()
        # parent_of with an id
        child = self.env.ref('base.res_partner_main1')
        sibling = self.env.ref('base.res_partner_main2')
        parent = self.env.ref('base.main_partner')
        parents = self.env['res.partner'].search([
            ('id', 'parent_of', child.id),
        ])
        self.assertItemsEqual(parents, parent + child)
        # parent_of with some many2one field
        siblings_and_parents = self.env['res.partner'].search([
            ('commercial_partner_id', 'parent_of', child.id),
        ])
        self.assertItemsEqual(
            siblings_and_parents, parent + child + sibling)
        # parent_of negated
        nonparents = self.env['res.partner'].search([
            '!',
            ('id', 'parent_of', child.id),
        ])
        self.assertFalse(parents & nonparents)
        # substring
        substring_matches = self.env['res.partner'].search([
            ('name', 'substring_of', ' YourCompany is great')
        ])
        self.assertTrue(substring_matches)
