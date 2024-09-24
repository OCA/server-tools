# Copyright 2024 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAuditlogLineAccessRule(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAuditlogLineAccessRule, cls).setUpClass()
        cls.group_user = cls.env.ref('base.group_user')
        cls.model = cls.env['ir.model'].create({
            'name': 'Test Model',
            'model': 'x_test_model_2',
        })
        cls.auditlog_rule = cls.env['auditlog.rule'].create({
            'name': 'Test Auditlog Rule',
            'model_id': cls.model.id,
        })
        cls.field = cls.env['ir.model.fields'].create({
            'name': 'x_test_field',
            'model_id': cls.model.id,
            'field_description': 'Test Field',
            'ttype': 'char',
        })

    def test_create_auditlog_line_access_rule(self):
        """Test the creation of an auditlog line access rule"""
        rule = self.env['auditlog.line.access.rule'].create({
            'name': 'Test Rule',
            'auditlog_rule_id': self.auditlog_rule.id,
            'field_ids': [(6, 0, [self.field.id])],
        })
        self.assertTrue(rule)
        # Verify if the default group is added
        self.assertIn(self.group_user, rule.group_ids)

    def test_write_auditlog_line_access_rule(self):
        """Test writing to an auditlog line access rule"""
        rule = self.env['auditlog.line.access.rule'].create({
            'name': 'Test Rule',
            'auditlog_rule_id': self.auditlog_rule.id,
        })
        rule.write({
            'field_ids': [(6, 0, [self.field.id])],
        })
        self.assertIn(self.field, rule.field_ids)
        # Verify if rules are regenerated
        self.assertTrue(rule.get_linked_rules())

    def test_unlink_auditlog_line_access_rule(self):
        """Test unlinking of an auditlog line access rule"""
        rule = self.env['auditlog.line.access.rule'].create({
            'name': 'Test Rule',
            'auditlog_rule_id': self.auditlog_rule.id,
        })
        linked_rule = self.env['ir.rule'].create({
            'name': 'Linked Rule',
            'model_id': self.model.id,
            'domain_force': '[]',
            'auditlog_line_access_rule_id': rule.id,
        })
        rule.unlink()
        self.assertFalse(linked_rule.exists())

    def test_add_default_group_if_needed(self):
        """Test adding default group if needed"""
        rule = self.env['auditlog.line.access.rule'].create({
            'name': 'Test Rule',
            'auditlog_rule_id': self.auditlog_rule.id,
            'field_ids': [(6, 0, [self.field.id])],
            'group_ids': [],
        })
        rule.add_default_group_if_needed()
        self.assertIn(self.group_user, rule.group_ids)

    def test_regenerate_rules(self):
        """Test regenerating rules"""
        rule = self.env['auditlog.line.access.rule'].create({
            'name': 'Test Rule',
            'auditlog_rule_id': self.auditlog_rule.id,
            'group_ids': [(6, 0, [self.group_user.id])],
        })
        rule.regenerate_rules()
        linked_rules = rule.get_linked_rules()
        self.assertTrue(linked_rules)

    def test_prepare_rule_values(self):
        """Test preparation of rule values"""
        rule = self.env['auditlog.line.access.rule'].create({
            'name': 'Test Rule',
            'auditlog_rule_id': self.auditlog_rule.id,
            'group_ids': [(6, 0, [self.group_user.id])],
        })
        values = rule._prepare_rule_values()
        self.assertGreater(len(values), 0)
        self.assertIn('domain_force', values[0])
