# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import ProgrammingError
from openerp.tools import config
from openerp.tests.common import TransactionCase


class TestDatabaseCleanup(TransactionCase):
    def test_database_cleanup(self):
        # create an orphaned column
        self.cr.execute(
            'alter table res_users add column database_cleanup_test int')
        purge_columns = self.env['cleanup.purge.wizard.column'].create({})
        purge_columns.purge_all()
        # must be removed by the wizard
        with self.assertRaises(ProgrammingError):
            with self.registry.cursor() as cr:
                cr.execute('select database_cleanup_test from res_users')

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
        self.env['ir.model'].create({
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
        self.env['ir.module.module'].create({
            'name': 'database_cleanup_test',
            'state': 'to upgrade',
        })
        purge_modules = self.env['cleanup.purge.wizard.module'].create({})
        # this reloads our registry, and we don't want to run tests twice
        config.options['test_enable'] = False
        purge_modules.purge_all()
        config.options['test_enable'] = True
        # must be removed by the wizard
        self.assertFalse(self.env['ir.module.module'].search([
            ('name', '=', 'database_cleanup_test'),
        ]))

        # create an orphaned table
        self.env.cr.execute('create table database_cleanup_test (test int)')
        purge_tables = self.env['cleanup.purge.wizard.table'].create({})
        purge_tables.purge_all()
        with self.assertRaises(ProgrammingError):
            with self.registry.cursor() as cr:
                self.env.cr.execute('select * from database_cleanup_test')
