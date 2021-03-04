# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models
from odoo.tests.common import SavepointCase


class BaseKanbanAbstractTester(models.TransientModel):
    _name = 'base.kanban.abstract.tester'
    _inherit = 'base.kanban.abstract'


class TestBaseKanbanAbstract(SavepointCase):

    @classmethod
    def _init_test_model(cls, model_cls):
        """ It builds a model from model_cls in order to test abstract models.

        Note that this does not actually create a table in the database, so
        there may be some unidentified edge cases.

        Args:
            model_cls (openerp.models.BaseModel): Class of model to initialize
        Returns:
            model_cls: Instance
        """
        registry = cls.env.registry
        cr = cls.env.cr
        inst = model_cls._build_model(registry, cr)
        model = cls.env[model_cls._name].with_context(todo=[])
        model._prepare_setup()
        model._setup_base(partial=False)
        model._setup_fields(partial=False)
        model._setup_complete()
        model._auto_init()
        model.init()
        model._auto_end()
        cls.test_model_record = cls.env['ir.model'].search([
            ('name', '=', model._name),
        ])
        return inst

    @classmethod
    def setUpClass(cls):
        super(TestBaseKanbanAbstract, cls).setUpClass()
        cls.env.registry.enter_test_mode()
        cls._init_test_model(BaseKanbanAbstractTester)
        cls.test_model = cls.env[BaseKanbanAbstractTester._name]

    def setUp(self):
        super(TestBaseKanbanAbstract, self).setUp()
        test_stage_1 = self.env['base.kanban.stage'].create({
            'name': 'Test Stage 1',
            'res_model_id': self.test_model_record.id,
        })
        test_stage_2 = self.env['base.kanban.stage'].create({
            'name': 'Test Stage 2',
            'res_model_id': self.test_model_record.id,
            'fold': True,
        })

        self.id_1 = test_stage_1.id
        self.id_2 = test_stage_2.id

    def test_read_group_stage_ids_base_case(self):
        """It should return a structure with the proper content"""
        self.assertEqual(
            self.test_model._read_group_stage_ids(),
            (
                [(self.id_1, 'Test Stage 1'), (self.id_2, 'Test Stage 2')],
                {self.id_1: False, self.id_2: True},
            )
        )

    def test_read_group_stage_ids_correct_associated_model(self):
        """It should only return info for stages with right associated model"""
        stage_model = self.env['ir.model'].search([
            ('model', '=', 'base.kanban.stage'),
        ])
        self.env['base.kanban.stage'].create({
            'name': 'Test Stage 3',
            'res_model_id': stage_model.id,
        })

        self.assertEqual(
            self.test_model._read_group_stage_ids(),
            (
                [(self.id_1, 'Test Stage 1'), (self.id_2, 'Test Stage 2')],
                {self.id_1: False, self.id_2: True},
            )
        )

    def test_default_stage_id(self):
        """ It should return an empty RecordSet """
        self.assertEqual(
            self.env['base.kanban.abstract']._default_stage_id(),
            self.env['base.kanban.stage']
        )
