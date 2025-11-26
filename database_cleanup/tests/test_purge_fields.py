# Copyright 2021 Camptocamp SA
# Copyright 2024 360ERP (https://www.360erp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import tagged

from .common import Common, environment


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeFields(Common):
    def setUp(self):
        super().setUp()
        # Setup field in the same environment context as the test
        self.model_name = "x_database.cleanup.test.field.model"
        self.field_name = "x_database_cleanup_test_field"

    def test_empty_field(self):
        with environment() as env:
            # Create test model and field in same transaction
            model_values = {
                "name": "Database cleanup test field-model",
                "model": self.model_name,
            }
            model = env["ir.model"].create(model_values)
            env.cr.execute(
                "insert into ir_attachment (name, res_model, res_id, type) values "
                "('test attachment', %s, 42, 'binary')",
                [self.model_name],
            )

            # create a nonexistent field
            field_values = {
                "name": self.field_name,
                "model_id": model.id,
                "field_description": "Database cleanup test field",
                "ttype": "boolean",
            }
            field = env["ir.model.fields"].create(field_values)

            env.cr.execute(
                "update ir_model_fields set state = 'base' where id = %s ",
                [field.id],
            )

            # Create wizard with the field to purge manually
            wizard = env["cleanup.purge.wizard.field"].create(
                {
                    "purge_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": self.field_name,
                                "field_id": field.id,
                            },
                        )
                    ]
                }
            )
            wizard.purge_all()
            # must be removed by the wizard
            self.assertFalse(
                env["ir.model.fields"].search(
                    [
                        ("name", "=", self.field_name),
                    ]
                )
            )

            # Cleanup model
            model_to_clean = env["ir.model"].search([("model", "=", self.model_name)])
            if model_to_clean:
                model_to_clean.unlink()
