# Copyright 2021 Camptocamp SA
# Copyright 2024 360ERP (https://www.360erp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo.tests.common import tagged

from .common import Common, environment


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeFields(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with environment() as env:
            # create a nonexistent model
            cls.model_name = "x_database.cleanup.test.field.model"
            cls.model_values = {
                "name": "Database cleanup test field-model",
                "model": cls.model_name,
            }
            cls.model = env["ir.model"].create(cls.model_values)
            cls.attachment_content = b"Database cleanup field-purge attachment"
            # Use a real stored file: model deletion schedules it for garbage
            # collection, which requires a valid filestore path.
            with patch.object(
                type(env["ir.attachment"]), "_storage", return_value="file"
            ):
                attachment = (
                    env["ir.attachment"]
                    .sudo()
                    .create(
                        {
                            "name": "test attachment",
                            "res_model": cls.model_name,
                            "res_id": 42,
                            "raw": cls.attachment_content,
                        }
                    )
                )
            cls.attachment_id = attachment.id

            # create a nonexistent field
            cls.field_name = "x_database_cleanup_test_field"
            cls.field_values = {
                "name": cls.field_name,
                "model_id": cls.model.id,
                "field_description": "Database cleanup test field",
                "ttype": "boolean",
            }
            cls.field = env["ir.model.fields"].create(cls.field_values)

            env.cr.execute(
                "update ir_model_fields set state = 'base' where id = %s ",
                [cls.field.id],
            )
            env.registry.models[cls.model_name]._fields__.pop(cls.field_name)

    def test_empty_field(self):
        with environment() as env:
            attachment = env["ir.attachment"].sudo().browse(self.attachment_id)
            self.assertTrue(attachment.store_fname)
            self.assertEqual(attachment.raw.content, self.attachment_content)
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
        # Run after committing the model deletion, as the web test suite does.
        # An invalid attachment path must not break a later suite's teardown.
        with environment() as env:
            env["ir.attachment"]._gc_file_store_unsafe(grace_period=0)
