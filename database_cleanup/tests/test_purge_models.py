# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import tagged

from .common import Common


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeLineColumn(Common):
    def setUp(self):
        super(TestCleanupPurgeLineColumn, self).setUp()
        # create a nonexistent model
        self.model_name = "x_database.cleanup.test.model"
        self.model_values = {
            "name": "Database cleanup test model",
            "model": self.model_name,
        }
        self.model = self.env["ir.model"].create(self.model_values)
        self.env.cr.execute(
            "insert into ir_attachment (name, res_model, res_id, type) values "
            "('test attachment', %s, 42, 'binary')",
            [self.model_name],
        )
        self.env.registry.models.pop(self.model_name)

    def tearDown(self):
        """We recreate the model to avoid registry Exception at loading"""
        super(TestCleanupPurgeLineColumn, self).tearDown()
        # FIXME: issue origin is not clear but it must be addressed.
        self.model = self.env["ir.model"].create(self.model_values)

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
