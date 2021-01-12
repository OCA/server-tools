# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import ProgrammingError

from odoo.tools import mute_logger

from .common import Common


class TestCleanupPurgeLineColumn(Common):
    def setUp(self):
        super(TestCleanupPurgeLineColumn, self).setUp()
        # create an orphaned column
        self.env.cr.execute(
            "alter table res_partner add column database_cleanup_test int"
        )

    def test_empty_column(self):
        # We need use a model that is not blocked (Avoid use res.users)
        partner_model = self.env["ir.model"].search(
            [("model", "=", "res.partner")], limit=1
        )
        wizard = self.env["cleanup.purge.wizard.column"].create(
            {
                "purge_line_ids": [
                    (
                        0,
                        0,
                        {"model_id": partner_model.id, "name": "database_cleanup_test"},
                    )
                ]
            }
        )
        wizard.purge_all()
        # must be removed by the wizard
        with self.assertRaises(ProgrammingError):
            with self.env.registry.cursor() as cr:
                with mute_logger("odoo.sql_db"):
                    cr.execute("select database_cleanup_test from res_partner")
