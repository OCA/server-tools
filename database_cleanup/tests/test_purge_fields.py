# Copyright 2021 Camptocamp SA
# Copyright 2024 360ERP (https://www.360erp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import tagged

from .common import Common, environment


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeFields(Common):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        with environment() as env:
            # create a nonexistent model
            self.model_name = "x_database.cleanup.test.field.model"
            self.model_values = {
                "name": "Database cleanup test field-model",
                "model": self.model_name,
            }
            self.model = env["ir.model"].create(self.model_values)
            env.cr.execute(
                "insert into ir_attachment (name, res_model, res_id, type) values "
                "('test attachment', %s, 42, 'binary')",
                [self.model_name],
            )

            # create a nonexistent field
            self.field_name = "x_database_cleanup_test_field"
            self.field_values = {
                "name": self.field_name,
                "model_id": self.model.id,
                "field_description": "Database cleanup test field",
                "ttype": "boolean",
            }
            self.field = env["ir.model.fields"].create(self.field_values)

            env.cr.execute(
                "update ir_model_fields set state = 'base' where id = %s ",
                [self.field.id],
            )
            env.registry.models[self.model_name]._fields.pop(self.field_name)

    def test_empty_field(self):
        with environment() as env:
            wizard = env["cleanup.purge.wizard.field"].create({})
            wizard.purge_all()
            # must be removed by the wizard
            self.assertFalse(
                env["ir.model.fields"].search(
                    [
                        ("name", "=", self.field_name),
                    ]
                )
            )

    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        with environment() as env:
            model = env["ir.model"].search([("model", "=", self.model_name)])
            if model:
                model.unlink()
