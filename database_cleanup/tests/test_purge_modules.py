# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import threading

from odoo.tools import config

from .common import Common


class TestCleanupPurgeLineModule(Common):
    def setUp(self):
        super(TestCleanupPurgeLineModule, self).setUp()
        # create a nonexistent module
        self.module = self.env["ir.module.module"].create(
            {
                "name": "database_cleanup_test",
                "state": "to upgrade",
            }
        )

    def test_remove_to_upgrade_module(self):
        wizard = self.env["cleanup.purge.wizard.module"].create({})
        config.options["test_enable"] = False  # Maybe useless now ?!
        self.patch(threading.currentThread(), "testing", False)
        wizard.purge_all()
        config.options["test_enable"] = True  # Maybe useless now ?!
        self.patch(threading.currentThread(), "testing", True)
        # must be removed by the wizard
        self.assertFalse(
            self.env["ir.module.module"].search(
                [
                    ("name", "=", "database_cleanup_test"),
                ]
            )
        )
