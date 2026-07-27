# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestGlobalUndoTour(HttpCase):
    def test_undo_redo_from_the_systray(self):
        """The OWL systray and the Ctrl+Z hotkey drive the server round trip."""
        admin = self.env.ref("base.user_admin")
        # Start from an empty stack so the tour's Ctrl+Z can only hit our step.
        self.env["global.undo.transaction"].search([]).unlink()
        # Journalled exactly like a user request: not sudo, own transaction step.
        self.env(user=admin)["res.partner"].create({"name": "GU Tour Partner"})
        step = self.env["global.undo.transaction"].search([])
        self.assertEqual(step.name, "Created Contact: GU Tour Partner")

        self.start_tour("/odoo", "global_undo_tour", login="admin")

        self.assertEqual(
            step.state, "undone", "the last hotkey undo should have unwound the step"
        )
        self.assertFalse(
            self.env["res.partner"].search([("name", "=", "GU Tour Partner")]),
            "the contact should be gone again after the keyboard undo",
        )
