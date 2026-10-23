from odoo.tests.common import TransactionCase


class TestBaseKanbanAbstract(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Stage = cls.env["base.kanban.stage"]
        cls.stage_model = cls.env["ir.model"].search(
            [("model", "=", "base.kanban.stage")], limit=1
        )
        cls.stage_1 = cls.Stage.create(
            {
                "name": "Test Stage 1",
                "res_model_id": cls.stage_model.id,
                "sequence": 1,
            }
        )
        cls.stage_2 = cls.Stage.create(
            {
                "name": "Test Stage 2",
                "res_model_id": cls.stage_model.id,
                "sequence": 2,
            }
        )

    def test_stage_creation(self):
        self.assertEqual(self.stage_1.sequence, 1)

    def test_stage_ordering(self):
        stages = self.Stage.search(
            [("res_model_id", "=", self.stage_model.id)], order="sequence"
        )
        self.assertEqual(stages[0], self.stage_1)

    def test_stage_fold(self):
        self.stage_1.fold = True
        self.assertTrue(self.stage_1.fold)
