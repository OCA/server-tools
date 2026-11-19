# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import tagged
from odoo.tools import sql

from .common import Common, environment


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeLineTable(Common):
    def test_empty_table(self):
        with environment() as env:
            # create an orphaned table
            env.cr.execute("create table database_cleanup_test (test int)")
            wizard = env["cleanup.purge.wizard.table"].create({})
            wizard.purge_all()
            self.assertFalse(sql.table_exists(env.cr, "database_cleanup_test"))

    def test_blacklist(self):
        """A table mentioned in the blacklist is not purged"""
        with environment() as env:
            env.cr.execute("create table if not exists endpoint_route (test int)")
            wizard = env["cleanup.purge.wizard.table"].create({})
            wizard.purge_all()
            self.assertTrue(sql.table_exists(env.cr, "endpoint_route"))

    def test_table_with_dependent_views(self):
        """Dependent views are dropped before their table."""
        with environment() as env:
            env.cr.execute("create table database_cleanup_test_view_source (test int)")
            env.cr.execute(
                "create view database_cleanup_test_view as "
                "select test from database_cleanup_test_view_source"
            )
            env.cr.execute(
                "create view database_cleanup_test_view_child as "
                "select test from database_cleanup_test_view"
            )
            wizard = env["cleanup.purge.wizard.table"].create({})
            wizard.purge_all()
            self.assertFalse(
                sql.table_exists(env.cr, "database_cleanup_test_view_source")
            )
            self.assertFalse(sql.table_exists(env.cr, "database_cleanup_test_view"))
            self.assertFalse(
                sql.table_exists(env.cr, "database_cleanup_test_view_child")
            )

    def test_table_inheritance(self):
        """Child tables are dropped before their parent."""
        with environment() as env:
            env.cr.execute("create table database_cleanup_a_parent (test int)")
            env.cr.execute(
                "create table database_cleanup_z_child (test int) "
                "inherits (database_cleanup_a_parent)"
            )
            wizard = env["cleanup.purge.wizard.table"].create({})
            wizard.purge_all()
            self.assertFalse(sql.table_exists(env.cr, "database_cleanup_a_parent"))
            self.assertFalse(sql.table_exists(env.cr, "database_cleanup_z_child"))

    def test_table_with_external_foreign_key(self):
        """Foreign keys from non-purged tables do not prevent the drop."""
        with environment() as env:
            env.cr.execute(
                "create table database_cleanup_a_fk_parent (id int primary key)"
            )
            env.cr.execute(
                "create table database_cleanup_z_fk_child ("
                "parent_id int references database_cleanup_a_fk_parent(id))"
            )
            wizard = env["cleanup.purge.wizard.table"].create(
                {
                    "purge_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "database_cleanup_a_fk_parent",
                                "table_type": "base",
                            },
                        )
                    ]
                }
            )
            wizard.purge_all()
            self.assertFalse(sql.table_exists(env.cr, "database_cleanup_a_fk_parent"))
            self.assertTrue(sql.table_exists(env.cr, "database_cleanup_z_fk_child"))
            env.cr.execute("drop table database_cleanup_z_fk_child")
