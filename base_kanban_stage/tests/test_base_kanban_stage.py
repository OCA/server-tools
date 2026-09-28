from odoo.tests.common import TransactionCase


class TestBaseKanbanStage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Stage = cls.env["base.kanban.stage"]
        cls.stage_model = cls.env["ir.model"].search(
            [("model", "=", "base.kanban.stage")], limit=1
        )

    def test_default_res_model_id_no_params(self):
        result = self.Stage._default_res_model_id()
        self.assertFalse(result)

    def test_default_res_model_id_with_context(self):
        result = self.Stage.with_context(
            default_res_model_id=self.stage_model.id
        )._default_res_model_id()
        self.assertEqual(result, self.stage_model.id)

    def test_create_auto_sequence(self):
        stage = self.Stage.create(
            {
                "name": "Auto Seq",
                "res_model_id": self.stage_model.id,
            }
        )
        self.assertTrue(stage.sequence > 0)

    def test_active_default(self):
        stage = self.Stage.create(
            {
                "name": "Active Test",
                "res_model_id": self.stage_model.id,
            }
        )
        self.assertTrue(stage.active)
