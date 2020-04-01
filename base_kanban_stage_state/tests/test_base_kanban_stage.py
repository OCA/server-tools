# Copyright 2017 Specialty Medical Drugstore
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestBaseKanbanStage(TransactionCase):
    def test_get_states(self):
        """It should return a list of stages"""
        test_stage = self.env["base.kanban.stage"].with_context({})

        self.assertEqual(
            test_stage._get_states(),
            [
                ("draft", "New"),
                ("open", "In Progress"),
                ("pending", "Pending"),
                ("done", "Done"),
                ("cancelled", "Cancelled"),
                ("exception", "Exception"),
            ],
        )
