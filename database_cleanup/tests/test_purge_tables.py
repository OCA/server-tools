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
