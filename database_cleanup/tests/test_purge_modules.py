# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import tagged

from .common import Common, environment


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeLineModule(Common):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.model_name = "database_cleanup_test"
        with environment() as env:
            # Clean up any existing test module from previous runs
            # Use SQL to avoid state validation issues
            env.cr.execute(
                "DELETE FROM ir_model_data WHERE model = 'ir.module.module' "
                "AND name = %s",
                ["module_" + self.model_name],
            )
            env.cr.execute(
                "DELETE FROM ir_module_module WHERE name = %s", [self.model_name]
            )
            # create a nonexistent module
            self.module = env["ir.module.module"].create(
                {
                    "name": self.model_name,
                    "state": "to upgrade",
                }
            )

    def test_remove_to_upgrade_module(self):
        with environment() as env:
            wizard = env["cleanup.purge.wizard.module"].create({})
            module_names = wizard.purge_line_ids.filtered(
                lambda x: not x.purged
            ).mapped("name")
            self.assertTrue(self.model_name in module_names)

    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        with environment() as env:
            # Clean up test module using SQL to avoid state validation
            env.cr.execute(
                "DELETE FROM ir_model_data WHERE model = 'ir.module.module' "
                "AND name = %s",
                ["module_" + self.model_name],
            )
            env.cr.execute(
                "DELETE FROM ir_module_module WHERE name = %s", [self.model_name]
            )
