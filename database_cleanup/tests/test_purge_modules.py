# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import tagged

from .common import Common, environment


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeLineModule(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_name = "database_cleanup_test"
        with environment() as env:
            # create a nonexistent module
            cls.module = env["ir.module.module"].create(
                {
                    "name": cls.model_name,
                    "state": "to upgrade",
                }
            )
            # create an ir.model.data pointing to a non-existent field
            cls.orphan_field_data = env["ir.model.data"].create(
                {
                    "name": "x_orphan_field",
                    "module": cls.model_name,
                    "model": "ir.model.fields",
                    "res_id": 999999,  # nonexistent record
                    "noupdate": True,
                }
            )

    def test_remove_to_upgrade_module(self):
        with environment() as env:
            wizard = env["cleanup.purge.wizard.module"].create({})
            module_names = wizard.purge_line_ids.filtered(
                lambda x: not x.purged
            ).mapped("name")
            self.assertTrue(self.model_name in module_names)

    def test_module_data_uninstall_removes_orphans(self):
        with environment() as env:
            IrModelData = env["ir.model.data"]

            self.assertTrue(
                IrModelData.browse(self.orphan_field_data.id).exists(),
                "orphan field data should exist before uninstall",
            )

            IrModelData._module_data_uninstall([self.model_name])

            self.assertFalse(
                IrModelData.browse(self.orphan_field_data.id).exists(),
                "orphan field data should be removed after uninstall",
            )

    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        with environment() as env:
            module = env["ir.module.module"].search([("name", "=", self.model_name)])
            if module:
                module.state = "uninstalled"
                module.unlink()
