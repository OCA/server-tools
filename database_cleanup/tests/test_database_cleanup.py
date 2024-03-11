# Copyright 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from contextlib import contextmanager
from psycopg2 import ProgrammingError
from odoo.modules.registry import Registry
from odoo.tools import config, mute_logger
from odoo.tests.common import TransactionCase, tagged


# Use post_install to get all models loaded, more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestDatabaseCleanup(TransactionCase):
    def setUp(self):
        super(TestDatabaseCleanup, self).setUp()
        self.modules = self.env["ir.module.module"]
        self.models = self.env["ir.model"]
        # Create one property for tests
        self.env["ir.property"].create(
            {
                "fields_id": self.env.ref("base.field_res_partner__name").id,
                "type": "char",
                "value_text": "My default partner name",
            }
        )

    def test_recreate_index(self):
        # delete some index and check if our module recreated it
        self.env.cr.execute("drop index res_partner_name_index")
        create_indexes = self.env["cleanup.create_indexes.wizard"].create({})
        create_indexes.purge_all()
        self.env.cr.execute(
            "select indexname from pg_indexes "
            "where indexname='res_partner_name_index' and "
            "tablename='res_partner'"
        )
        self.assertEqual(self.env.cr.rowcount, 1)

    def test_purge_duplicate_property(self):
        # check if duplicate a property is deleted
        duplicate_property = self.env["ir.property"].search([], limit=1).copy()
        purge_property = self.env["cleanup.purge.wizard.property"].create({})
        purge_property.purge_all()
        self.assertFalse(duplicate_property.exists())

    def test_purge_obsolete_columns(self):
        # create an orphaned column
        self.env.cr.execute(
            "alter table res_partner add column database_cleanup_test int")
        # We need use a model that is not blocked (Avoid use res.users)
        partner_model = self.env["ir.model"].search(
            [("model", "=", "res.partner")], limit=1)
        purge_columns = self.env["cleanup.purge.wizard.column"].create(
            {"purge_line_ids": [
                (0, 0, {"model_id": partner_model.id,
                        "name": "database_cleanup_test"})]}
        )
        purge_columns.purge_all()
        # must be removed by the wizard
        with self.assertRaises(ProgrammingError):
            with self.env.registry.cursor() as cr:
                with mute_logger("odoo.sql_db"):
                    cr.execute("select database_cleanup_test from res_partner")

    def test_purge_obsolete_columns_ignore_inherited(self):
        """ Inherited columns have to be ignored because they cannot be deleted """

        # Create an inherited table
        self.env.cr.execute(
            "CREATE table dbcleanup_inherited_test (database_cleanup_test2 int) "
            "INHERITS (res_partner)"
            )

        # We need use a model that inherits from another
        client_action_model = self.env["ir.model"].search(
            [("model", "=", "ir.actions.act_window")], limit=1)
        # Add name column (wich is inherited) to columns to remove
        purge_columns = self.env["cleanup.purge.wizard.column"].create(
            {"purge_line_ids": [
                (0, 0, {"model_id": client_action_model.id,
                        "name": "name"})]}
        )
        purge_columns.purge_all()
        # the column must not be removed by the wizard
        with self.env.registry.cursor() as cr:
            with mute_logger("odoo.sql_db"):
                # this query must be executed without error
                cr.execute("select name from ir_act_window")

    def test_purge_obsolete_data(self):
        # create a data entry pointing nowhere
        self.env.cr.execute("select max(id) + 1 from res_users")
        self.env["ir.model.data"].create(
            {
                "module": "database_cleanup",
                "name": "test_no_data_entry",
                "model": "res.users",
                "res_id": self.env.cr.fetchone()[0],
            }
        )
        purge_data = self.env["cleanup.purge.wizard.data"].create({})
        purge_data.purge_all()
        # must be removed by the wizard
        with self.assertRaises(ValueError):
            self.env.ref("database_cleanup.test_no_data_entry")

    def test_purge_obsolete_model(self):
        # create a nonexistent model
        self.models = self.env["ir.model"].create(
            {"name": "Database cleanup test model",
                "model": "x_database.cleanup.test.model"}
        )
        # and a cronjob for it
        cronjob = self.env["ir.cron"].create(
            {"name": "testcronjob", "model_id": self.models.id})
        self.env.cr.execute(
            "insert into ir_attachment (name, res_model, res_id, type) values "
            "('test attachment', 'database.cleanup.test.model', 42, 'binary')"
        )
        self.env.registry.models.pop("x_database.cleanup.test.model")
        purge_models = self.env["cleanup.purge.wizard.model"].create({})
        purge_models.purge_all()
        # must be removed by the wizard
        self.assertFalse(self.env["ir.model"].search(
            [("model", "=", "x_database.cleanup.test.model")]))
        self.assertFalse(cronjob.exists())

    def test_purge_obsolete_table(self):
        # create an orphaned table
        self.env.cr.execute("create table database_cleanup_test (test int)")
        purge_tables = self.env["cleanup.purge.wizard.table"].create({})
        purge_tables.purge_all()
        with self.assertRaises(ProgrammingError):
            with self.env.registry.cursor() as cr:
                with mute_logger("odoo.sql_db"):
                    cr.execute("select * from database_cleanup_test")

    def test_purge_obsolete_module(self):
        @contextmanager
        def keep_registry():
            """purging a module resets the registry, so here we keep a
            reference to our original registry, as we don't want to run tests
            twice and need the original for further tests"""
            original_registry = Registry.registries[self.env.cr.dbname]
            config.options["test_enable"] = False
            yield
            config.options["test_enable"] = True
            # reset afterwards
            Registry.registries[self.env.cr.dbname] = original_registry

        # create nonexistent modules in different states
        self.modules += self.env["ir.module.module"].create(
            {"name": "database_cleanup_test_to_upgrade", "state": "to upgrade"}
        )
        self.modules += self.env["ir.module.module"].create(
            {"name": "database_cleanup_test_uninstalled", "state": "uninstalled"}
        )

        with keep_registry(), mute_logger("odoo.modules.graph", "odoo.modules.loading"):
            purge_modules = self.env["cleanup.purge.wizard.module"].create({})
            # this module should be purged already during default_get
            self.assertFalse(self.env["ir.module.module"].search(
                [("name", "=", "database_cleanup_test_uninstalled")]))

        with keep_registry(), mute_logger("odoo.modules.graph", "odoo.modules.loading"):
            purge_modules.purge_all()
            # must be removed by the wizard
            self.assertFalse(self.env["ir.module.module"].search(
                [("name", "=", "database_cleanup_test_to_upgrade")]))

    def tearDown(self):
        super(TestDatabaseCleanup, self).tearDown()
        with self.registry.cursor() as cr2:
            # Release blocked tables with pending deletes
            self.env.cr.rollback()
            if self.modules:
                cr2.execute(
                    "DELETE FROM ir_module_module WHERE id in %s",
                    (tuple(self.modules.ids),))
            if self.models:
                cr2.execute("DELETE FROM ir_model WHERE id in %s",
                            (tuple(self.models.ids),))
            cr2.commit()

            cr2.execute(
                "DELETE FROM ir_model_data where name like '%database_cleanup_test%'")
