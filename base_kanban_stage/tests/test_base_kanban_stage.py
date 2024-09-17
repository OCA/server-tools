# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestBaseKanbanStage(TransactionCase):
    def test_default_res_model_id_no_params(self):
        """It should return empty ir.model Recordset if no params in context"""
        test_stage = self.env["base.kanban.stage"].with_context({})
        res_model_id = test_stage._default_res_model_id()

        self.assertFalse(res_model_id)
        self.assertEqual(res_model_id._name, "ir.model")

    def test_default_res_model_id_no_action(self):
        """It should return empty ir.model Recordset if no action in params"""
        test_stage = self.env["base.kanban.stage"].with_context(params={})
        res_model_id = test_stage._default_res_model_id()

        self.assertFalse(res_model_id)
        self.assertEqual(res_model_id._name, "ir.model")

    def test_default_res_model_id_info_in_context(self):
        """It should return correct ir.model record if info in context"""
        test_action = self.env["ir.actions.act_window"].create(
            {"name": "Test Action", "res_model": "res.users"}
        )
        test_stage = self.env["base.kanban.stage"].with_context(
            params={"action": test_action.id},
        )

        self.assertEqual(
            test_stage._default_res_model_id(),
            self.env["ir.model"].search([("model", "=", "res.users")]),
        )

    def test_default_res_model_id_ignore_self(self):
        """It should not return ir.model record corresponding to stage model"""
        test_action = self.env["ir.actions.act_window"].create(
            {"name": "Test Action", "res_model": "base.kanban.stage"}
        )
        test_stage = self.env["base.kanban.stage"].with_context(
            params={"action": test_action.id},
        )

        self.assertFalse(test_stage._default_res_model_id())
