# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# Copyright 2020 InitOS Gmbh.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from odoo.tests import common

TEST_MODEL_NAME = 'base.kanban.abstract.tester'


class BaseKanbanAbstractTester(models.Model):
    _name = 'base.kanban.abstract.tester'
    _inherit = 'base.kanban.abstract'


class TestBaseKanbanAbstract(common.SavepointCase):

    def _init_test_model(cls, model_cls):
        registry = cls.env.registry
        cls.env.cr.execute(
            "INSERT INTO ir_model (model, name) VALUES (%s, %s)",
            (TEST_MODEL_NAME, 'Test AEAT model'),
        )
        model_cls._build_model(registry, cls.env.cr)
        model = cls.env[model_cls._name].with_context(todo=[])
        model._prepare_setup()
        model._setup_base()
        model._setup_fields()
        model._setup_complete()
        model._auto_init()
        model.init()
        return model

    def setUp(self):
        super(TestBaseKanbanAbstract, self).setUp()
        self.registry.enter_test_mode()
        self.old_cursor = self.cr
        self.cr = self.registry.cursor()
        self.env = api.Environment(self.cr, self.uid, {})
        self.test_model = self._init_test_model(BaseKanbanAbstractTester)
        test_model_record = self.env['ir.model'].search([
            ('model', '=', self.test_model._name),
        ])
        self.test_stage = self.env['base.kanban.stage'].create({
            'name': 'Test Stage',
            'res_model_id': test_model_record.id,
            'sequence': 2,
        })
        self.test_stage_2 = self.env['base.kanban.stage'].create({
            'name': 'Test Stage 2',
            'res_model_id': test_model_record.id,
            'sequence': 1,
        })

    def tearDown(self):
        self.registry.leave_test_mode()
        self.registry[self.test_model._name]._abstract = True
        self.registry[self.test_model._name]._auto = False
        self.cr = self.old_cursor
        self.env = api.Environment(self.cr, self.uid, {})

        super(TestBaseKanbanAbstract, self).tearDown()

    def test_default_stage_id_no_stages(self):
        """It should return empty recordset when model has no stages"""
        self.env['base.kanban.stage'].search([
            ('res_model_id.model', '=', self.test_model._name),
        ]).unlink()
        result = self.test_model._default_stage_id()

        self.assertEqual(result, self.env['base.kanban.stage'])

    def test_default_stage_id_available_stages(self):
        """It should return lowest sequence stage when model has stages"""
        result = self.test_model._default_stage_id()
        self.assertEqual(result, self.test_stage_2)

    def test_read_group_stage_ids(self):
        """It should return all corresponding stages in requested sort order"""
        result = self.test_model._read_group_stage_ids(
            self.env['base.kanban.stage'], None, 'id'
        )

        expected = self.env['base.kanban.stage'].search(
            [('res_model_id.model', '=', self.test_model._name)],
            order='id',
        )
        self.assertEqual(result[0], expected[0])
        self.assertEqual(result[1], expected[1])
