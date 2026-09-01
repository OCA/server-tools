# Copyright 2016-2017 LasLabs Inc.
# Copyright 2025 ForgeFlow.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models
from odoo.tests.common import TransactionCase


class BaseKanbanAbstractTester(models.Model):
    _name = "base.kanban.abstract.tester"
    _description = "base kanban abstract tester"
    _inherit = "base.kanban.abstract"
    _order = "id asc"


class TestBaseKanbanAbstract(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Manually register and build the test model
        from odoo.orm import model_classes

        registry = cls.env.registry
        cr = cls.env.cr

        # Build the model if not already in registry
        if BaseKanbanAbstractTester._name not in registry.models:
            # Add the model definition to registry
            model_classes.add_to_registry(registry, BaseKanbanAbstractTester)

            # Setup models
            registry._setup_models__(cr, [BaseKanbanAbstractTester._name])

            # Initialize the model
            with cls.muted_registry_logger:
                registry.init_models(
                    cr, [BaseKanbanAbstractTester._name], {}, install=False
                )

        cls.test_model = cls.env[BaseKanbanAbstractTester._name]

    def setUp(self):
        super().setUp()
        test_model_record = self.env["ir.model"].search(
            [
                ("model", "=", self.test_model._name),
            ],
            limit=1,
        )
        self.assertEqual(len(test_model_record), 1)
        self.test_stage = self.env["base.kanban.stage"].create(
            {
                "name": "Test Stage",
                "res_model_id": test_model_record.id,
                "sequence": 2,
            }
        )
        self.test_stage_2 = self.env["base.kanban.stage"].create(
            {
                "name": "Test Stage 2",
                "res_model_id": test_model_record.id,
                "sequence": 1,
            }
        )

    def tearDown(self):
        self.registry[self.test_model._name]._abstract = True
        self.registry[self.test_model._name]._auto = False
        super().tearDown()

    def test_default_stage_id_no_stages(self):
        """It should return empty recordset when model has no stages"""
        self.env["base.kanban.stage"].search(
            [
                ("res_model_id.model", "=", self.test_model._name),
            ]
        ).unlink()
        result = self.test_model._default_stage_id()

        self.assertEqual(result, self.env["base.kanban.stage"])

    def test_default_stage_id_available_stages(self):
        """It should return lowest sequence stage when model has stages"""
        result = self.test_model._default_stage_id()

        self.assertEqual(result, self.test_stage_2)

    def test_read_group_stage_ids(self):
        """It should return all corresponding stages in requested sort order"""
        result = self.test_model._read_group_stage_ids(
            self.env["base.kanban.stage"], None
        )

        expected = self.env["base.kanban.stage"].search(
            [("res_model_id.model", "=", self.test_model._name)],
        )
        self.assertEqual(result[0], expected[0])
        self.assertEqual(result[1], expected[1])
