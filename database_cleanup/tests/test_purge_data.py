# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import tagged

from .common import Common, environment


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeLineData(Common):
    def setUp(self):
        super().setUp()
        with environment() as env:
            # create a data entry pointing nowhere
            env.cr.execute("select max(id) + 1 from res_users")
            env["ir.model.data"].create(
                {
                    "module": "database_cleanup",
                    "name": "test_no_data_entry",
                    "model": "res.users",
                    "res_id": env.cr.fetchone()[0],
                }
            )

    def test_pointing_nowhere(self):
        with environment() as env:
            wizard = env["cleanup.purge.wizard.data"].create({})
            wizard.purge_all()
            # must be removed by the wizard
            with self.assertRaises(ValueError):
                env.ref("database_cleanup.test_no_data_entry")
