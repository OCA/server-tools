# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Journalling and replay of ordinary create / write / unlink operations."""

import base64

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import GlobalUndoCase

# A 1x1 transparent GIF: the smallest thing that proves binaries survive a
# round trip through the trash.
TINY_GIF = base64.b64encode(
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
    b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00"
    b"\x02\x02D\x01\x00;"
)


@tagged("post_install", "-at_install")
class TestGlobalUndoCrud(GlobalUndoCase):
    def test_group_is_implied_for_internal_users(self):
        self.assertTrue(self.user.has_group("global_undo.global_undo_group_user"))

    def test_create_undo_redo(self):
        partner = self.uenv["res.partner"].create(
            {"name": "GU Partner", "city": "Girona"}
        )
        self.assertTrue(
            self.Transaction.with_env(self.uenv).gu_state()["undo"],
            "the creation was not journalled",
        )

        self.assertTrue(self.undo()["done"])
        self.assertFalse(partner.exists(), "undoing a creation must delete the record")

        self.assertTrue(self.redo()["done"])
        operation = self.Operation.with_env(self.uenv).search(
            [("res_id", "=", partner.id), ("kind", "=", "create")], limit=1
        )
        restored = self.uenv["res.partner"].browse(operation.restored_res_id)
        self.assertEqual(restored.name, "GU Partner")
        self.assertEqual(restored.city, "Girona")

    def test_write_undo_restores_every_changed_field(self):
        partner = self.uenv["res.partner"].create(
            {"name": "GU Partner", "city": "Girona"}
        )
        self.step()
        partner.write({"city": "Barcelona", "comment": "<p>hello</p>"})

        self.assertTrue(self.undo()["done"])
        partner.invalidate_recordset()
        self.assertEqual(partner.city, "Girona")
        self.assertFalse(partner.comment)

    def test_a_new_operation_discards_the_redo_stack(self):
        self.uenv["res.partner"].create({"name": "GU Partner"})
        self.undo()
        self.assertTrue(self.Transaction.with_env(self.uenv)._gu_next("redo"))

        self.step()
        self.uenv["res.partner"].create({"name": "GU Discarder"})
        self.assertFalse(
            self.Transaction.with_env(self.uenv)._gu_next("redo"),
            "history written after an undo must make the redo unreachable",
        )

    def test_many2many_round_trip(self):
        partner = self.uenv["res.partner"].create({"name": "GU Partner"})
        tag = self.uenv["res.partner.category"].create({"name": "GU Tag"})
        self.step()
        partner.write({"category_id": [(4, tag.id)]})

        self.assertTrue(self.undo()["done"])
        partner.invalidate_recordset()
        self.assertNotIn(tag, partner.category_id)

    def test_delete_restore_and_full_cycle(self):
        victim = self.uenv["res.partner"].create(
            {
                "name": "GU Victim",
                "phone": "+34 600 000 000",
                "image_1920": TINY_GIF,
            }
        )
        victim_id = victim.id
        self.step()
        victim.unlink()

        operation = self.Operation.with_env(self.uenv).search(
            [("kind", "=", "unlink"), ("res_id", "=", victim_id)]
        )
        self.assertTrue(operation.in_trash)

        self.assertTrue(self.undo()["done"])
        operation.invalidate_recordset()
        self.assertFalse(operation.in_trash)
        restored = self.uenv["res.partner"].browse(operation.restored_res_id)
        self.assertEqual(restored.phone, "+34 600 000 000")
        self.assertEqual(restored.image_1920, TINY_GIF, "the image was not restored")

        # Redoing the deletion must put the record back in the trash, not leave
        # a dangling id behind.
        self.assertTrue(self.redo()["done"])
        operation.invalidate_recordset()
        self.assertFalse(operation.restored_res_id)
        self.assertTrue(operation.in_trash)

        self.assertTrue(self.undo()["done"])
        operation.invalidate_recordset()
        self.assertTrue(
            self.uenv["res.partner"].browse(operation.restored_res_id).exists()
        )

    def test_trash_restore_keeps_children_attached_to_their_parent(self):
        parent = self.uenv["res.partner"].create({"name": "GU Parent"})
        child = self.uenv["res.partner"].create(
            {"name": "GU Child", "parent_id": parent.id}
        )
        parent_id, child_id = parent.id, child.id
        self.step()
        (child + parent).unlink()

        trash = self.Operation.with_env(self.uenv).search([("in_trash", "=", True)])
        self.assertEqual(len(trash), 2)
        trash.action_restore()

        restored = {operation.res_id: operation.restored_res_id for operation in trash}
        restored_child = self.uenv["res.partner"].browse(restored[child_id])
        self.assertEqual(
            restored_child.parent_id.id,
            restored[parent_id],
            "a child restored next to its parent must follow the parent's new id",
        )

    def test_a_concurrent_edit_blocks_the_undo(self):
        partner = self.uenv["res.partner"].create({"name": "GU Partner"})
        self.step()
        partner.write({"function": "Tester"})
        operation = self.Operation.with_env(self.uenv).search(
            [("res_id", "=", partner.id), ("kind", "=", "write")], limit=1
        )

        # Somebody else edits the record afterwards.
        self.uenv.flush_all()
        self.env.cr.execute(
            "UPDATE res_partner SET write_date = write_date "
            "+ interval '1 second' WHERE id = %s",
            (partner.id,),
        )
        partner.invalidate_recordset()

        self.assertIn("changed after", operation._gu_blocker("undo") or "")
        self.assertFalse(self.undo()["done"])

    def test_undoing_a_creation_also_respects_concurrent_edits(self):
        partner = self.uenv["res.partner"].create({"name": "GU Partner"})
        operation = self.Operation.with_env(self.uenv).search(
            [("res_id", "=", partner.id), ("kind", "=", "create")], limit=1
        )

        self.uenv.flush_all()
        self.env.cr.execute(
            "UPDATE res_partner SET write_date = write_date "
            "+ interval '1 second' WHERE id = %s",
            (partner.id,),
        )
        partner.invalidate_recordset()

        self.assertIn(
            "changed after",
            operation._gu_blocker("undo") or "",
            "deleting the record would discard the other user's edit",
        )

    def test_a_step_that_creates_then_writes_can_still_be_undone(self):
        """The write moves write_date past what the creation recorded."""
        partner = self.uenv["res.partner"].create({"name": "GU Partner"})
        partner.write({"city": "Girona"})
        self.assertTrue(self.undo()["done"])
        self.assertFalse(partner.exists())

    def test_another_user_cannot_undo_my_step(self):
        self.uenv["res.partner"].create({"name": "GU Partner"})
        other = self.env["res.users"].create(
            {
                "name": "GU Other",
                "login": "gu_other",
                "groups_id": [(4, self.env.ref("base.group_user").id)],
            }
        )
        step = self.Transaction.with_env(self.uenv).search(
            [("user_id", "=", self.user.id)], limit=1
        )
        with self.assertRaises(UserError):
            step.with_user(other)._gu_apply("undo")

    def test_technical_models_stay_out_of_the_journal(self):
        before = self.Transaction.search_count([])
        self.uenv["ir.config_parameter"].sudo().set_param("gu.probe", "1")
        self.assertEqual(
            self.Transaction.search_count([]), before, "ir.* leaked into the journal"
        )

    def test_superuser_work_is_not_journalled(self):
        before = self.Transaction.search_count([])
        self.env["res.partner"].sudo().create({"name": "GU Sudo"})
        self.assertEqual(self.Transaction.search_count([]), before)

    def test_mass_updates_are_skipped(self):
        partners = self.uenv["res.partner"].create(
            [{"name": f"GU Bulk {index}"} for index in range(3)]
        )
        self.step()
        before = self.Transaction.search_count([])
        # The cap is on the recordset size, so a stub recordset is enough.
        huge = self.uenv["res.partner"].browse(range(1, 300))
        self.assertFalse(huge._gu_is_tracked(), "a mass update must not be journalled")
        self.assertEqual(self.Transaction.search_count([]), before)
        self.assertTrue(partners.exists())
