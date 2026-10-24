# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo import api
from odoo.tests.common import tagged

from .common import Common, environment


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeLineColumn(Common):
    def _check_model_attachments(self, superuser=False):
        suffix = "superuser" if superuser else "settings"
        model_name = f"x_database.cleanup.test.{suffix}"
        contents = (
            b"Visible model attachment",
            b"Shared ordinary and binary-field attachment",
            b"Shared ordinary and binary-field attachment",
            b"Unrelated partner attachment",
        )
        with environment() as admin_env:
            model = admin_env["ir.model"].create(
                {"name": "Database cleanup test model", "model": model_name}
            )
            Attachment = admin_env["ir.attachment"]
            partner_id = admin_env.ref("base.partner_admin").id
            with patch.object(type(Attachment), "_storage", return_value="file"):
                attachments = Attachment.create(
                    [
                        {
                            "name": "Visible model attachment",
                            "res_model": model_name,
                            "raw": contents[0],
                        },
                        {
                            "name": "Orphaned record attachment",
                            "res_model": model_name,
                            "res_id": 42,
                            "raw": contents[1],
                        },
                        {
                            "name": "Binary field attachment",
                            "res_model": model_name,
                            "res_field": "x_binary",
                            "res_id": 42,
                            "raw": contents[2],
                        },
                        {
                            "name": "Unrelated partner attachment",
                            "res_model": "res.partner",
                            "res_id": partner_id,
                            "raw": contents[3],
                        },
                    ]
                )
            attachment_ids = attachments.ids
            self.assertTrue(all(attachment.store_fname for attachment in attachments))
            self.assertEqual(attachments[1].store_fname, attachments[2].store_fname)
            # Prime the cache before SQL detachment; purge must invalidate it.
            self.assertEqual(attachments[:2].mapped("res_model"), [model_name] * 2)
            admin_env.registry.models.pop(model_name)
            env = (
                admin_env
                if superuser
                else admin_env(user=admin_env.ref("base.user_admin"), su=False)
            )
            self.assertEqual(env.su, superuser)
            self.assertTrue(env.is_system())
            # Settings users cannot see the orphaned record attachment, and
            # the default search excludes field attachments even for root.
            self.assertEqual(
                set(env["ir.attachment"].search([("res_model", "=", model_name)]).ids),
                set(attachment_ids[:2] if superuser else attachment_ids[:1]),
            )
            wizard = env["cleanup.purge.wizard.model"].create({})
            wizard.purge_all()
            self.assertFalse(model.exists())
            self.assertEqual(
                attachments.exists().ids, attachment_ids[:2] + attachment_ids[3:]
            )
            self.assertEqual(attachments[:2].mapped("res_model"), [False, False])
            self.assertEqual(attachments[1].res_id, 42)
            self.assertEqual(attachments[3].res_model, "res.partner")
            self.assertEqual(attachments[3].res_id, partner_id)

        # Model deletion is committed before GC. In particular, deleting the
        # field attachment must not remove the file still used by its sibling.
        with environment() as env:
            env["ir.attachment"]._gc_file_store_unsafe(grace_period=0)
        with environment() as env:
            remaining = env["ir.attachment"].browse(attachment_ids).exists()
            self.assertEqual(remaining.ids, attachment_ids[:2] + attachment_ids[3:])
            self.assertEqual(remaining[:2].mapped("res_model"), [False, False])
            self.assertEqual(remaining[-1].res_model, "res.partner")
            self.assertEqual(remaining[-1].res_id, partner_id)
            self.assertEqual(
                [attachment.raw.content for attachment in remaining],
                [contents[0], contents[1], contents[3]],
            )
            remaining.unlink()

    def test_empty_model(self):
        self._check_model_attachments()

    def test_empty_model_as_superuser(self):
        self._check_model_attachments(superuser=True)

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
