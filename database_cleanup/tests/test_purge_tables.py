# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import ProgrammingError

from odoo.tests.common import tagged
from odoo.tools import mute_logger

from .common import Common


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeLineTable(Common):
    def setUp(self):
        super(TestCleanupPurgeLineTable, self).setUp()
        # create an orphaned table
        self.env.cr.execute("create table database_cleanup_test (test int)")

    def test_empty_table(self):
        wizard = self.env["cleanup.purge.wizard.table"].create({})
        wizard.purge_all()
        with self.assertRaises(ProgrammingError):
            with self.env.registry.cursor() as cr:
                with mute_logger("odoo.sql_db"):
                    cr.execute("select * from database_cleanup_test")
