# -*- coding: utf-8 -*-
# © 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestChangesetFieldRule(common.TransactionCase):

    def setUp(self):
        super(TestChangesetFieldRule, self).setUp()
        self.company_model_id = self.env.ref('base.model_res_company').id
        self.field_name = self.env.ref('base.field_res_partner_name')
        self.field_street = self.env.ref('base.field_res_partner_street')

    def test_get_rules(self):
        ChangesetFieldRule = self.env['changeset.field.rule']
        ChangesetFieldRule.search([]).unlink()
        rule1 = ChangesetFieldRule.create({
            'field_id': self.field_name.id,
            'action': 'validate',
        })
        rule2 = ChangesetFieldRule.create({
            'field_id': self.field_street.id,
            'action': 'never',
        })
        get_rules = ChangesetFieldRule.get_rules(None)
        self.assertEqual(get_rules, {'name': rule1, 'street': rule2})

    def test_get_rules_source(self):
        ChangesetFieldRule = self.env['changeset.field.rule']
        ChangesetFieldRule.search([]).unlink()
        rule1 = ChangesetFieldRule.create({
            'field_id': self.field_name.id,
            'action': 'validate',
        })
        rule2 = ChangesetFieldRule.create({
            'field_id': self.field_street.id,
            'action': 'never',
        })
        rule3 = ChangesetFieldRule.create({
            'source_model_id': self.company_model_id,
            'field_id': self.field_street.id,
            'action': 'never',
        })
        model = ChangesetFieldRule
        rules = model.get_rules(None)
        self.assertEqual(rules, {u'name': rule1, u'street': rule2})
        rules = model.get_rules('res.company')
        self.assertEqual(rules, {u'name': rule1, u'street': rule3})

    def test_get_rules_cache(self):
        ChangesetFieldRule = self.env['changeset.field.rule']
        ChangesetFieldRule.search([]).unlink()
        rule = ChangesetFieldRule.create({
            'field_id': self.field_name.id,
            'action': 'validate',
        })
        self.assertEqual(
            ChangesetFieldRule.get_rules(None)['name'].action,
            'validate',
        )
        # Write on cursor to bypass the cache invalidation for the
        # matter of the test
        self.env.cr.execute("UPDATE changeset_field_rule "
                            "SET action = 'never' "
                            "WHERE id = %s", (rule.id,))
        self.assertEqual(
            ChangesetFieldRule.get_rules(None)['name'].action,
            'validate',
        )
        rule.action = 'auto'
        self.assertEqual(
            ChangesetFieldRule.get_rules(None)['name'].action,
            'auto',
        )
        rule.unlink()
        self.assertFalse(ChangesetFieldRule.get_rules(None))
