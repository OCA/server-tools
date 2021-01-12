# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import Common


class TestCleanupPurgeLineData(Common):
    def setUp(self):
        super(TestCleanupPurgeLineData, self).setUp()
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

    def test_pointing_nowhere(self):
        wizard = self.env["cleanup.purge.wizard.data"].create({})
        wizard.purge_all()
        # must be removed by the wizard
        with self.assertRaises(ValueError):
            self.env.ref("database_cleanup.test_no_data_entry")
