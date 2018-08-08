# © 2015 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestAuditlog(object):

    def test_LogCreation(self):
        """First test, caching some data."""

        self.groups_rule.subscribe()

        auditlog_log = self.env['auditlog.log']
        group = self.env['res.groups'].create({
            'name': 'testgroup1',
        })
        self.assertTrue(auditlog_log.search([
            ('model_id', '=', self.groups_model_id),
            ('method', '=', 'create'),
            ('res_id', '=', group.id),
        ]).ensure_one())
        group.write({'name': 'Testgroup1'})
        self.assertTrue(auditlog_log.search([
            ('model_id', '=', self.groups_model_id),
            ('method', '=', 'write'),
            ('res_id', '=', group.id),
        ]).ensure_one())
        group.unlink()
        self.assertTrue(auditlog_log.search([
            ('model_id', '=', self.groups_model_id),
            ('method', '=', 'unlink'),
            ('res_id', '=', group.id),
        ]).ensure_one())

    def test_LogCreation2(self):
        """Second test, using cached data of the first one."""

        self.groups_rule.subscribe()

        auditlog_log = self.env['auditlog.log']
        testgroup2 = self.env['res.groups'].create({
            'name': 'testgroup2',
        })
        self.assertTrue(auditlog_log.search([
            ('model_id', '=', self.groups_model_id),
            ('method', '=', 'create'),
            ('res_id', '=', testgroup2.id),
        ]).ensure_one())

    def test_LogCreation3(self):
        """Third test, two groups, the latter being the parent of the former.
        Then we remove it right after (with (2, X) tuple) to test the creation
        of a 'write' log with a deleted resource (so with no text
        representation).
        """

        self.groups_rule.subscribe()
        auditlog_log = self.env['auditlog.log']
        testgroup3 = self.env['res.groups'].create({
            'name': 'testgroup3',
        })
        testgroup4 = self.env['res.groups'].create({
            'name': 'testgroup4',
            'implied_ids': [(4, testgroup3.id)],
        })
        testgroup4.write({'implied_ids': [(2, testgroup3.id)]})
        self.assertTrue(auditlog_log.search([
            ('model_id', '=', self.groups_model_id),
            ('method', '=', 'create'),
            ('res_id', '=', testgroup3.id),
        ]).ensure_one())
        self.assertTrue(auditlog_log.search([
            ('model_id', '=', self.groups_model_id),
            ('method', '=', 'create'),
            ('res_id', '=', testgroup4.id),
        ]).ensure_one())
        self.assertTrue(auditlog_log.search([
            ('model_id', '=', self.groups_model_id),
            ('method', '=', 'write'),
            ('res_id', '=', testgroup4.id),
        ]).ensure_one())


class TestAuditlogFull(TransactionCase, TestAuditlog):

    def setUp(self):
        super(TestAuditlogFull, self).setUp()
        self.groups_model_id = self.env.ref('base.model_res_groups').id
        self.groups_rule = self.env['auditlog.rule'].create({
            'name': 'testrule for groups',
            'model_id': self.groups_model_id,
            'log_read': True,
            'log_create': True,
            'log_write': True,
            'log_unlink': True,
            'log_type': 'full',
        })

    def tearDown(self):
        self.groups_rule.unlink()
        super(TestAuditlogFull, self).tearDown()


class TestAuditlogFast(TransactionCase, TestAuditlog):

    def setUp(self):
        super(TestAuditlogFast, self).setUp()
        self.groups_model_id = self.env.ref('base.model_res_groups').id
        self.groups_rule = self.env['auditlog.rule'].create({
            'name': 'testrule for groups',
            'model_id': self.groups_model_id,
            'log_read': True,
            'log_create': True,
            'log_write': True,
            'log_unlink': True,
            'log_type': 'fast',
        })

    def tearDown(self):
        self.groups_rule.unlink()
        super(TestAuditlogFast, self).tearDown()


class TestAuditlogFieldRules(TransactionCase):

    def setUp(self):
        super(TestAuditlogFieldRules, self).setUp()
        self.partner_model_id = self.env.ref('base.model_res_partner').id
        self.partner_rule = self.env['auditlog.rule'].create({
            'name': 'testrule for fields',
            'model_id': self.partner_model_id,
            'log_read': False,
            'log_create': False,
            'log_write': False,
            'log_unlink': False,
            'log_type': 'full',
            'field_rule_ids': [
                self.get_field_rule_line("res.partner", "vat", False, True),
                self.get_field_rule_line("res.partner", "ref", True, False),
            ],
        })
        pass

    def get_field_rule_line(self, model, field,
            read=False, write=False, create=False, unlink=False):
        return (0, 0, {
            'field_id': self.env['ir.model.fields'].search([
                ('name', '=', field),
                ('model', '=', model)], limit=1).id,
            'log_read': read,
            'log_write': write,
            'log_create': create,
            'log_unlink': unlink,
        })

    def test_LogCreationPerField(self):
        """Testing creating logs per field."""

        self.partner_rule.subscribe()

        auditlog_log = self.env['auditlog.log']
        partner = self.env['res.partner'].create({
            'name': 'testgroup1',
        })
        self.assertEqual(auditlog_log.search_count([
            ('model_id', '=', self.partner_model_id),
            ('method', '=', 'write'),
            ('res_id', '=', partner.id),
        ]), 0)
        partner.write({'name': 'New group name'})
        self.assertEqual(auditlog_log.search_count([
            ('model_id', '=', self.partner_model_id),
            ('method', '=', 'write'),
            ('res_id', '=', partner.id),
        ]), 0)
        partner.write({'vat': '1234567'})
        self.assertEqual(auditlog_log.search_count([
            ('model_id', '=', self.partner_model_id),
            ('method', '=', 'write'),
            ('res_id', '=', partner.id),
        ]), 1)
        count_read_logs = auditlog_log.search_count([
            ('model_id', '=', self.partner_model_id),
            ('method', '=', 'read'),
            ('res_id', '=', partner.id),
        ])
        self.env['res.partner'].search_read(
            domain=[('id', '=', partner.id)],
            fields=['name'],
        )
        self.assertEqual(auditlog_log.search_count([
            ('model_id', '=', self.partner_model_id),
            ('method', '=', 'read'),
            ('res_id', '=', partner.id),
        ]), count_read_logs)

        self.env['res.partner'].search_read(
            domain=[('id', '=', partner.id)],
            fields=['ref'],
        )
        self.assertEqual(auditlog_log.search_count([
            ('model_id', '=', self.partner_model_id),
            ('method', '=', 'read'),
            ('res_id', '=', partner.id),
        ]), count_read_logs + 1)
        partner.unlink()

    def tearDown(self):
        self.partner_rule.unlink()
        super(TestAuditlogFieldRules, self).tearDown()
