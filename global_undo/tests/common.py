# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase


class GlobalUndoCase(TransactionCase):
    """Shared setup: an ordinary user whose operations are journalled.

    The journal ignores superuser work, so the tests must act as a real user.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Transaction = cls.env["global.undo.transaction"]
        cls.Operation = cls.env["global.undo.operation"]
        cls.user = cls.env["res.users"].create(
            {
                "name": "Global Undo Tester",
                "login": "gu_tester",
                "groups_id": [
                    (4, cls.env.ref("base.group_user").id),
                    # The tests journal contacts, which need this to be created.
                    (4, cls.env.ref("base.group_partner_manager").id),
                ],
            }
        )
        cls.uenv = cls.env(user=cls.user)

    def step(self):
        """Close the current step so the next operations form a new one.

        A step is one user request; a test is one cursor, so it has to be said
        explicitly here.
        """
        self.env.cr.gu_transaction_id = False

    def undo(self):
        return self.Transaction.with_env(self.uenv).gu_apply_next("undo")

    def redo(self):
        return self.Transaction.with_env(self.uenv).gu_apply_next("redo")
