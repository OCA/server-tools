from odoo.tests import common


class TestKanbanStage(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.stage_model = self.env["base.kanban.stage"]
        self.user_model = self.env["res.users"]
        self.model_model = self.env["ir.model"]

        # Create a test user
        self.test_user = self.user_model.create(
            {
                "name": "Test User",
                "login": "test@example.com",
            }
        )

        # Create a test model
        self.test_model = self.model_model.create(
            {
                "name": "Test Model",
                "model": "test.model",
            }
        )

    def test_stage_creation(self):
        stage = self.stage_model.create(
            {
                "name": "Test Stage",
                "model_id": self.test_model.id,
            }
        )
        self.assertEqual(stage.name, "Test Stage")

    def test_stage_with_user(self):
        stage = self.stage_model.create(
            {
                "name": "Test Stage with User",
                "model_id": self.test_model.id,
                "user_id": self.test_user.id,
            }
        )
        self.assertEqual(stage.user_id, self.test_user)

    def test_stage_sequence(self):
        stage1 = self.stage_model.create(
            {
                "name": "First Stage",
                "model_id": self.test_model.id,
                "sequence": 10,
            }
        )
        stage2 = self.stage_model.create(
            {
                "name": "Second Stage",
                "model_id": self.test_model.id,
                "sequence": 20,
            }
        )
        self.assertEqual(stage1.sequence, 10)
        self.assertEqual(stage2.sequence, 20)

    def test_stage_model_relation(self):
        stage = self.stage_model.create(
            {
                "name": "Test Stage",
                "model_id": self.test_model.id,
            }
        )
        self.assertEqual(stage.model_id, self.test_model)

    def test_stage_default_values(self):
        stage = self.stage_model.create(
            {
                "name": "Default Stage",
                "model_id": self.test_model.id,
            }
        )
        self.assertTrue(stage.active)
        self.assertEqual(stage.sequence, 10)
        self.assertFalse(stage.fold)

    def test_stage_copy(self):
        stage = self.stage_model.create(
            {
                "name": "Test Stage",
                "model_id": self.test_model.id,
            }
        )
        stage_copy = stage.copy()
        self.assertEqual(stage_copy.name, "Test Stage (copy)")
        self.assertEqual(stage_copy.model_id, stage.model_id)
