# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import tagged

from .common import Common


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeLineColumn(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create a nonexistent model
        cls.model_name = "x_database.cleanup.test.model"
        cls.model_values = {
            "name": "Database cleanup test model",
            "model": cls.model_name,
        }
        cls.model = cls.env["ir.model"].create(cls.model_values)
        cls.env.cr.execute(
            "insert into ir_attachment (name, res_model, res_id, type) values "
            "('test attachment', %s, 42, 'binary')",
            [cls.model_name],
        )
        cls.env.registry.models.pop(cls.model_name)

    @classmethod
    def tearDownClass(cls):
        """We recreate the model to avoid registry Exception at loading"""
        super().tearDownClass()
        # FIXME: issue origin is not clear but it must be addressed.
        cls.model = cls.env["ir.model"].create(cls.model_values)

    def test_empty_model(self):
        wizard = self.env["cleanup.purge.wizard.model"].create({})
        wizard.purge_all()
        # must be removed by the wizard
        self.assertFalse(
            self.env["ir.model"].search(
                [
                    ("model", "=", self.model_name),
                ]
            )
        )
