# Copyright 2026 Cetmix
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import os
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests.common import tagged

from .common import Common, environment


@tagged("post_install", "-at_install")
class TestCleanupPurgeLineAttachment(Common):
    @classmethod
    def setUpClass(cls):
        """Create two ir.attachment records; delete backing file of one (orphan)."""
        super().setUpClass()
        with environment() as env:
            IrAttachment = env["ir.attachment"]
            datas = base64.b64encode(b"test_orphan").decode("ascii")
            orphan = IrAttachment.create(
                {
                    "name": "test_orphan_attachment.txt",
                    "type": "binary",
                    "datas": datas,
                }
            )
            datas_valid = base64.b64encode(b"test_valid").decode("ascii")
            valid = IrAttachment.create(
                {
                    "name": "test_valid_attachment.txt",
                    "type": "binary",
                    "datas": datas_valid,
                }
            )
            # Delete backing file to create orphan
            full_path = IrAttachment._full_path(orphan.store_fname)
            os.unlink(full_path)
            cls.orphan_attach_id = orphan.id
            cls.valid_attach_id = valid.id

    def test_find_orphaned_attachments(self):
        """Assert wizard find() includes orphan in purge lines, excludes valid."""
        with environment() as env:
            wizard = env["cleanup.purge.wizard.attachment"].create({})
            line_attachment_ids = wizard.purge_line_ids.mapped("attachment_id").ids
            self.assertIn(self.orphan_attach_id, line_attachment_ids)
            self.assertNotIn(self.valid_attach_id, line_attachment_ids)

    def test_find_does_not_prefetch_unrequested_attachment_fields(self):
        """find() must not prefetch every ir.attachment column."""
        with environment() as env:
            ir_model = env.registry["ir.attachment"]
            original_read = ir_model._read
            store_fname_fields = []

            def tracking_read(records, fields):
                if "store_fname" in fields:
                    store_fname_fields.append(set(fields))
                return original_read(records, fields)

            with patch.object(ir_model, "_read", tracking_read):
                env["cleanup.purge.wizard.attachment"].create({})

            self.assertTrue(store_fname_fields)
            allowed = {"store_fname", "name"}
            for fnames in store_fname_fields:
                extra = fnames - allowed
                self.assertFalse(
                    extra,
                    "find() prefetched unrequested attachment fields: %s" % extra,
                )

    def test_find_evicts_processed_batches_from_cache(self):
        """Processed search_read batches must leave the ORM cache."""
        with environment() as env:
            IrAttachment = env["ir.attachment"]
            datas = base64.b64encode(b"batch").decode("ascii")
            for index in range(3):
                IrAttachment.create(
                    {
                        "name": "test_find_batch_%s.txt" % index,
                        "type": "binary",
                        "datas": datas,
                    }
                )
            store_fname_field = IrAttachment._fields["store_fname"]
            name_field = IrAttachment._fields["name"]
            prior_batch_ids = []
            nonempty_batches = []
            IrModel = env.registry["ir.attachment"]
            original_search_read = IrModel.search_read

            def tracking_search_read(records, *args, **kwargs):
                for attach_id in prior_batch_ids:
                    rec = IrAttachment.browse(attach_id)
                    self.assertFalse(env.cache.contains(rec, store_fname_field))
                    self.assertFalse(env.cache.contains(rec, name_field))
                rows = original_search_read(records, *args, **kwargs)
                if rows:
                    prior_batch_ids[:] = [row["id"] for row in rows]
                    nonempty_batches.append(len(rows))
                return rows

            with patch(
                "odoo.addons.database_cleanup.models.purge_attachments."
                "ATTACHMENT_FIND_BATCH",
                2,
            ), patch.object(IrModel, "search_read", tracking_search_read):
                env["cleanup.purge.wizard.attachment"].find()

            self.assertGreaterEqual(len(nonempty_batches), 2)
            self.assertTrue(all(size <= 2 for size in nonempty_batches))

    def test_purge_orphaned_attachments(self):
        """Assert purge_all() removes orphan record, leaves valid intact."""
        with environment() as env:
            wizard = env["cleanup.purge.wizard.attachment"].create({})
            wizard.purge_all()
            orphan = env["ir.attachment"].browse(self.orphan_attach_id)
            valid = env["ir.attachment"].browse(self.valid_attach_id)
            self.assertFalse(orphan.exists())
            self.assertTrue(valid.exists())

    def test_purge_skips_protected_attachment(self):
        """When unlink raises UserError on one line, purge others and skip."""
        with environment() as env:
            IrAttachment = env["ir.attachment"]
            datas_a = base64.b64encode(b"test_protected").decode("ascii")
            orphan_protected = IrAttachment.create(
                {
                    "name": "test_protected_orphan.txt",
                    "type": "binary",
                    "datas": datas_a,
                }
            )
            datas_b = base64.b64encode(b"test_unprotected").decode("ascii")
            orphan_other = IrAttachment.create(
                {
                    "name": "test_unprotected_orphan.txt",
                    "type": "binary",
                    "datas": datas_b,
                }
            )
            os.unlink(IrAttachment._full_path(orphan_protected.store_fname))
            os.unlink(IrAttachment._full_path(orphan_other.store_fname))

            protected_id = orphan_protected.id
            other_id = orphan_other.id

            IrModel = env.registry["ir.attachment"]
            original_unlink = IrModel.unlink

            def patched_unlink(self):
                if protected_id in self.ids:
                    # Dynamic message avoids translation lint on test-only UserError.
                    raise UserError(str(protected_id))
                return original_unlink(self)

            wizard = env["cleanup.purge.wizard.attachment"].create(
                {
                    "purge_line_ids": [
                        Command.create(
                            {
                                "attachment_id": protected_id,
                                "name": orphan_protected.store_fname
                                or str(protected_id),
                            }
                        ),
                        Command.create(
                            {
                                "attachment_id": other_id,
                                "name": orphan_other.store_fname or str(other_id),
                            }
                        ),
                    ],
                }
            )
            protected_line = wizard.purge_line_ids.filtered(
                lambda l: l.attachment_id.id == protected_id
            )
            other_line = wizard.purge_line_ids.filtered(
                lambda l: l.attachment_id.id == other_id
            )
            protected_line_id = protected_line.id
            other_line_id = other_line.id

            with patch.object(IrModel, "unlink", patched_unlink):
                wizard.purge_line_ids.purge()

            Line = env["cleanup.purge.line.attachment"]
            self.assertFalse(Line.browse(protected_line_id).purged)
            self.assertTrue(Line.browse(other_line_id).purged)
            self.assertTrue(IrAttachment.browse(protected_id).exists())
            self.assertFalse(IrAttachment.browse(other_id).exists())
