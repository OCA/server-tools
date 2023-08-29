# Copyright 2016-2017 LasLabs Inc.
# Copyright 2019 ForgeFlow.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from collections import deque

from odoo import api, models
from odoo.tests.common import TransactionCase


class BaseKanbanAbstractTester(models.Model):
    _name = "base.kanban.abstract.tester"
    _description = "base kanban abstract tester"
    _inherit = "base.kanban.abstract"


class TestBaseKanbanAbstract(TransactionCase):
    def _init_test_model(self, model_cls):
        model_cls._build_model(self.registry, self.cr)
        model = self.env[model_cls._name]
        # setup_models():
        model._prepare_setup()
        model._setup_base()
        model._setup_fields()
        model._setup_complete()
        # init_models():
        self.registry._post_init_queue = deque()
        self.registry._foreign_keys = {}
        model._auto_init()
        model.init()
        self.env["ir.model"]._reflect_models([model._name])
        self.env["ir.model.fields"]._reflect_fields([model._name])
        self.env["ir.model.fields.selection"]._reflect_selections([model._name])
        self.env["ir.model.constraint"]._reflect_constraints([model._name])
        while self.registry._post_init_queue:
            func = self.registry._post_init_queue.popleft()
            func()
        del self.registry._post_init_queue
        del self.registry._foreign_keys
        return model

    def setUp(self):
        super(TestBaseKanbanAbstract, self).setUp()

        self.registry.enter_test_mode(self.cr)
        self.old_cursor = self.cr
        self.cr = self.registry.cursor()
        self.env = api.Environment(self.cr, self.uid, {})
        self.test_model = self._init_test_model(BaseKanbanAbstractTester)

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
        self.registry.leave_test_mode()
        self.registry[self.test_model._name]._abstract = True
        self.registry[self.test_model._name]._auto = False
        self.cr = self.old_cursor
        self.env = api.Environment(self.cr, self.uid, {})

        super(TestBaseKanbanAbstract, self).tearDown()

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
            self.env["base.kanban.stage"], None, "id"
        )

        expected = self.env["base.kanban.stage"].search(
            [("res_model_id.model", "=", self.test_model._name)],
            order="id",
        )
        self.assertEqual(result[0], expected[0])
        self.assertEqual(result[1], expected[1])
