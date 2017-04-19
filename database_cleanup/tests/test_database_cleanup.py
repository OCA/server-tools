# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import ProgrammingError
from openerp.modules.registry import RegistryManager
from openerp.tools import config
from openerp.tests.common import TransactionCase, at_install, post_install


# Use post_install to get all models loaded more info: odoo/odoo#13458
@at_install(False)
@post_install(True)
class TestDatabaseCleanup(TransactionCase):
    def setUp(self):
        super(TestDatabaseCleanup, self).setUp()
        self.module = None
        self.model = None

    def test_database_cleanup(self):
        # delete some index and check if our module recreated it
        self.env.cr.execute('drop index res_partner_name_index')
        create_indexes = self.env['cleanup.create_indexes.wizard'].create({})
        create_indexes.purge_all()
        self.env.cr.execute(
            'select indexname from pg_indexes '
            "where indexname='res_partner_name_index' and "
            "tablename='res_partner'"
        )
        self.assertEqual(self.env.cr.rowcount, 1)
        # duplicate a property
        duplicate_property = self.env['ir.property'].search([], limit=1).copy()
        purge_property = self.env['cleanup.purge.wizard.property'].create({})
        purge_property.purge_all()
        self.assertFalse(duplicate_property.exists())
        # create an orphaned column
        self.cr.execute(
            'alter table res_partner add column database_cleanup_test int')
        # We need use a model that is not blocked (Avoid use res.users)
        partner_model = self.env['ir.model'].search([
            ('model', '=', 'res.partner')], limit=1)
        purge_columns = self.env['cleanup.purge.wizard.column'].create({
            'purge_line_ids': [(0, 0, {
                'model_id': partner_model.id, 'name': 'database_cleanup_test'}
            )]})
        purge_columns.purge_all()
        # must be removed by the wizard
        with self.assertRaises(ProgrammingError):
            with self.registry.cursor() as cr:
                cr.execute('select database_cleanup_test from res_partner')

        # create a data entry pointing nowhere
        self.cr.execute('select max(id) + 1 from res_users')
        self.env['ir.model.data'].create({
            'module': 'database_cleanup',
            'name': 'test_no_data_entry',
            'model': 'res.users',
            'res_id': self.cr.fetchone()[0],
        })
        purge_data = self.env['cleanup.purge.wizard.data'].create({})
        purge_data.purge_all()
        # must be removed by the wizard
        with self.assertRaises(ValueError):
            self.env.ref('database_cleanup.test_no_data_entry')

        # create a nonexistent model
        self.model = self.env['ir.model'].create({
            'name': 'Database cleanup test model',
            'model': 'x_database.cleanup.test.model',
        })
        self.env.cr.execute(
            'insert into ir_attachment (name, res_model, res_id, type) values '
            "('test attachment', 'database.cleanup.test.model', 42, 'binary')")
        self.registry.models.pop('x_database.cleanup.test.model')
        self.registry._pure_function_fields.pop(
            'x_database.cleanup.test.model')
        purge_models = self.env['cleanup.purge.wizard.model'].create({})
        purge_models.purge_all()
        # must be removed by the wizard
        self.assertFalse(self.env['ir.model'].search([
            ('model', '=', 'x_database.cleanup.test.model'),
        ]))

        # create a nonexistent module
        self.module = self.env['ir.module.module'].create({
            'name': 'database_cleanup_test',
            'state': 'to upgrade',
        })
        purge_modules = self.env['cleanup.purge.wizard.module'].create({})
        # this reloads our registry, and we don't want to run tests twice
        # we also need the original registry for further tests, so save a
        # reference to it
        original_registry = RegistryManager.registries[self.env.cr.dbname]
        config.options['test_enable'] = False
        purge_modules.purge_all()
        config.options['test_enable'] = True
        # must be removed by the wizard
        self.assertFalse(self.env['ir.module.module'].search([
            ('name', '=', 'database_cleanup_test'),
        ]))
        # reset afterwards
        RegistryManager.registries[self.env.cr.dbname] = original_registry

        # create an orphaned table
        self.env.cr.execute('create table database_cleanup_test (test int)')
        purge_tables = self.env['cleanup.purge.wizard.table'].create({})
        purge_tables.purge_all()
        with self.assertRaises(ProgrammingError):
            with self.registry.cursor() as cr:
                self.env.cr.execute('select * from database_cleanup_test')

    def tearDown(self):
        super(TestDatabaseCleanup, self).tearDown()
        with self.registry.cursor() as cr2:
            # Release blocked tables with pending deletes
            self.env.cr.rollback()
            if self.module:
                cr2.execute(
                    "DELETE FROM ir_module_module WHERE id=%s",
                    (self.module.id,))
            if self.model:
                cr2.execute(
                    "DELETE FROM ir_model WHERE id=%s",
                    (self.model.id,))
            cr2.commit()
