# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import ProgrammingError

from odoo.tests.common import tagged
from odoo.tools import mute_logger

from .common import Common, environment


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeLineColumn(Common):
    def setUp(self):
        super().setUp()
        with environment() as env:
            # create an orphaned column
            env.cr.execute(
                "alter table res_partner add column database_cleanup_test int"
            )

    def test_empty_column(self):
        with environment() as env:
            # We need use a model that is not blocked (Avoid use res.users)
            partner_model = env["ir.model"].search(
                [("model", "=", "res.partner")], limit=1
            )
            wizard = env["cleanup.purge.wizard.column"].create(
                {
                    "purge_line_ids": [
                        (
                            0,
                            0,
                            {
                                "model_id": partner_model.id,
                                "name": "database_cleanup_test",
                            },
                        )
                    ]
                }
            )
            wizard.purge_all()
            # must be removed by the wizard
            with self.assertRaises(ProgrammingError):
                with env.registry.cursor() as cr:
                    with mute_logger("odoo.sql_db"):
                        cr.execute("select database_cleanup_test from res_partner")
