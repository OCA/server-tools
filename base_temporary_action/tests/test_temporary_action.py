# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase


class TestTemporaryAction(TransactionCase):
    def test_temporary_action(self):
        Actions = self.env["ir.actions.actions"]
        temporary_action = Actions.create(
            {
                "name": "temporary action",
                "type": "ir.actions.act_window",
                "is_temporary": True,
            }
        )
        Actions._gc_temporary_actions()
        self.assertTrue(
            temporary_action.exists(),
            "Action should still exists because it has not been created for more "
            "than one hour",
        )
        temporary_action.create_date = temporary_action.create_date - relativedelta(
            hours=1, seconds=1
        )
        Actions._gc_temporary_actions()
        self.assertFalse(temporary_action.exists())
