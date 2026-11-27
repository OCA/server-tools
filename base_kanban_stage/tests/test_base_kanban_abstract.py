# Copyright 2016-2017 LasLabs Inc.
# Copyright 2019 ForgeFlow.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models
from odoo.tests.common import TransactionCase


class BaseKanbanAbstractTester(models.Model):
    _name = "base.kanban.abstract.tester"
    _description = "base kanban abstract tester"
    _inherit = "base.kanban.abstract"


class TestBaseKanbanAbstract(TransactionCase):
    @classmethod
    def _init_test_model(cls, model_cls):
        registry = cls.registry
        model_cls._build_model(registry, cls.cr)
        registry.setup_models(cls.cr)
        registry.init_models(cls.cr, [model_cls._name], {}, install=False)
        model = cls.env[model_cls._name]
        cls.attrs_before[model._name] = set(vars(type(model)))
        cls.addClassCleanup(cls._remove_test_model, model_cls)
        return model

    @classmethod
    def _remove_test_model(cls, model_cls):
        registry = cls.registry
        for parent in ("base", "base.kanban.abstract"):
            registry[parent]._inherit_children.discard(model_cls._name)
        registry.models.pop(model_cls._name, None)
        module_models = models.MetaModel.module_to_models["base_kanban_stage"]
        if model_cls in module_models:
            module_models.remove(model_cls)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_model = cls._init_test_model(BaseKanbanAbstractTester)

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
