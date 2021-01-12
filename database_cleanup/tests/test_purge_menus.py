# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import Common


class TestCleanupPurgeLineMenu(Common):
    def setUp(self):
        super(TestCleanupPurgeLineMenu, self).setUp()
        # create a new empty menu
        self.menu = self.env["ir.ui.menu"].create({"name": "database_cleanup_test"})

    def test_empty_menu(self):
        wizard = self.env["cleanup.purge.wizard.menu"].create(
            {
                "purge_line_ids": [
                    (
                        0,
                        0,
                        {
                            "menu_id": self.menu.id,
                        },
                    )
                ]
            }
        )
        wizard.purge_all()
        self.assertFalse(
            self.env["ir.ui.menu"].search(
                [
                    ("name", "=", "database_cleanup_test"),
                ]
            )
        )
