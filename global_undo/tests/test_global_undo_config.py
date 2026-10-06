# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Administrator-facing configuration and history housekeeping."""

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import GlobalUndoCase


@tagged("post_install", "-at_install")
class TestGlobalUndoConfig(GlobalUndoCase):
    def test_an_excluded_model_is_no_longer_recorded(self):
        self.env["global.undo.exclusion"].create(
            {
                "model_id": self.env["ir.model"]._get("res.partner.category").id,
                "reason": "Tested here",
            }
        )
        before = self.Transaction.search_count([])
        self.uenv["res.partner.category"].create({"name": "GU Tag"})
        self.assertEqual(self.Transaction.search_count([]), before)

        # And recording resumes as soon as the exclusion is lifted.
        self.env["global.undo.exclusion"].search([]).unlink()
        self.uenv["res.partner.category"].create({"name": "GU Tag 2"})
        self.assertGreater(self.Transaction.search_count([]), before)

    def test_an_action_rule_must_name_methods_that_exist(self):
        with self.assertRaises(ValidationError):
            self.env["global.undo.action"].create(
                {
                    "model_id": self.env["ir.model"]._get("res.partner").id,
                    "method": "no_such_method",
                    "undo_methods": "write",
                }
            )

    def test_configured_actions_extend_and_override_the_defaults(self):
        Action = self.env["global.undo.action"]
        Action.create(
            {
                "model_id": self.env["ir.model"]._get("res.partner").id,
                "method": "toggle_active",
                "undo_methods": "toggle_active",
            }
        )
        self.assertEqual(
            Action._gu_registered()["res.partner"]["toggle_active"], ("toggle_active",)
        )

        # Archiving a rule for a shipped default switches that default off.
        if "sale.order" not in self.env:
            return
        self.assertIn("action_confirm", Action._gu_registered()["sale.order"])
        Action.create(
            {
                "model_id": self.env["ir.model"]._get("sale.order").id,
                "method": "action_confirm",
                "undo_methods": "action_draft",
                "active": False,
            }
        )
        self.assertNotIn(
            "action_confirm", Action._gu_registered().get("sale.order", {})
        )

    def test_vacuum_keeps_the_trash_after_the_history_expires(self):
        keeper = self.uenv["res.partner"].create({"name": "GU Vacuum Keeper"})
        self.step()
        keeper.unlink()
        self.step()
        plain = self.uenv["res.partner"].create({"name": "GU Vacuum Plain"})

        trashing, plain_step = self.Transaction.search([], limit=2, order="id desc")[
            ::-1
        ]
        self.assertTrue(trashing.operation_ids.filtered("in_trash"))

        # Both steps are older than the history window, neither than the trash one.
        old = fields.Datetime.now() - relativedelta(days=60)
        self.env.cr.execute(
            "UPDATE global_undo_transaction SET create_date = %s WHERE id IN %s",
            (old, tuple((trashing + plain_step).ids)),
        )
        (trashing + plain_step).invalidate_recordset()

        self.Transaction._gu_vacuum()
        self.assertFalse(plain_step.exists(), "expired history should be purged")
        self.assertTrue(
            trashing.exists(),
            "a step still holding a deleted record must survive the history window",
        )
        self.assertTrue(plain.exists())

    def test_vacuum_eventually_empties_the_trash(self):
        victim = self.uenv["res.partner"].create({"name": "GU Vacuum Victim"})
        self.step()
        victim.unlink()
        trashing = self.Transaction.search([], limit=1)

        self.env.cr.execute(
            "UPDATE global_undo_transaction SET create_date = %s WHERE id = %s",
            (fields.Datetime.now() - relativedelta(days=400), trashing.id),
        )
        trashing.invalidate_recordset()

        self.Transaction._gu_vacuum()
        self.assertFalse(trashing.exists())
