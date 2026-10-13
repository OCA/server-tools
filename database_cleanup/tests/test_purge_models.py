# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo import api
from odoo.tests.common import tagged

from .common import Common, environment


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeLineColumn(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with environment() as env:
            # create a nonexistent model
            cls.model_name = "x_database.cleanup.test.model"
            cls.model_values = {
                "name": "Database cleanup test model",
                "model": cls.model_name,
            }
            cls.model = env["ir.model"].create(cls.model_values)
            attachments = (
                env["ir.attachment"]
                .sudo()
                .create(
                    [
                        {
                            "name": "Visible model attachment",
                            "res_model": cls.model_name,
                        },
                        {
                            "name": "Orphaned record attachment",
                            "res_model": cls.model_name,
                            "res_id": 42,
                        },
                        {
                            "name": "Binary field attachment",
                            "res_model": cls.model_name,
                            "res_field": "x_binary",
                            "res_id": 42,
                        },
                    ]
                )
            )
            cls.attachment_ids = attachments.ids
            env.registry.models.pop(cls.model_name)

    def test_empty_model(self):
        with environment() as admin_env:
            env = admin_env(user=admin_env.ref("base.user_admin"), su=False)
            # Settings access is not sudo: attachments of missing records are
            # hidden, and binary-field attachments are excluded by the search.
            self.assertFalse(env.su)
            self.assertTrue(env.is_system())
            self.assertEqual(
                env["ir.attachment"].search([("res_model", "=", self.model_name)]).ids,
                self.attachment_ids[:1],
            )
            wizard = env["cleanup.purge.wizard.model"].create({})
            wizard.purge_all()
            # must be removed by the wizard
            self.assertFalse(
                env["ir.model"].search(
                    [
                        ("model", "=", self.model_name),
                    ]
                )
            )
            env.invalidate_all()
            remaining = env["ir.attachment"].sudo().browse(self.attachment_ids).exists()
            self.assertEqual(remaining.ids, self.attachment_ids[:1])
            self.assertFalse(remaining.res_model)
            remaining.unlink()

    def test_force_delete_keeps_ondelete_hooks(self):
        with environment() as env:
            model_name = "x_database.cleanup.test.ondelete"
            model = env["ir.model"].create(
                {"name": "Database cleanup ondelete test", "model": model_name}
            )
            # Simulate metadata left by an unavailable Python model.
            env.cr.execute(
                "UPDATE ir_model SET state = 'base' WHERE id = %s", [model.id]
            )
            model.invalidate_recordset(["state"])
            env.registry.models.pop(model_name)
            ondelete_calls = []

            @api.ondelete(at_uninstall=False)
            def check_ondelete(records):
                ondelete_calls.append(records.ids)
                self.assertTrue(records.env.context.get("force_delete"))
                self.assertFalse(records.pool.uninstalling_modules)

            with patch.object(
                type(model),
                "_ondelete_methods",
                [*model._ondelete_methods, check_ondelete],
            ):
                env["cleanup.purge.line.model"].create({"name": model_name}).purge()

            self.assertEqual(ondelete_calls, [model.ids])
            self.assertFalse(model.exists())
