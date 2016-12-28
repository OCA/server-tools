# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models
from openerp.tests.common import TransactionCase


class BaseKanbanAbstractTester(models.Model):
    _name = 'base.kanban.abstract.tester'
    _inherit = 'base.kanban.abstract'


class TestBaseKanbanAbstract(TransactionCase):
    def setUp(self):
        super(TestBaseKanbanAbstract, self).setUp()

        BaseKanbanAbstractTester._build_model(self.registry, self.cr)
        self.test_model = self.env[BaseKanbanAbstractTester._name]

        test_model_type = self.env['ir.model'].create({
            'model': BaseKanbanAbstractTester._name,
            'name': 'Kanban Abstract - Test Model',
            'state': 'base',
        })

        test_stage_1 = self.env['base.kanban.stage'].create({
            'name': 'Test Stage 1',
            'res_model': test_model_type.id,
        })
        test_stage_2 = self.env['base.kanban.stage'].create({
            'name': 'Test Stage 2',
            'res_model': test_model_type.id,
            'fold': True,
        })

        self.id_1 = test_stage_1.id
        self.id_2 = test_stage_2.id

    def test_read_group_stage_ids_base_case(self):
        '''It should return a structure with the proper content'''
        self.assertEqual(
            self.test_model._read_group_stage_ids(),
            (
                [(self.id_1, 'Test Stage 1'), (self.id_2, 'Test Stage 2')],
                {self.id_1: False, self.id_2: True},
            )
        )

    def test_read_group_stage_ids_correct_associated_model(self):
        '''It should only return info for stages with right associated model'''
        stage_model = self.env['ir.model'].search([
            ('model', '=', 'base.kanban.stage'),
        ])
        self.env['base.kanban.stage'].create({
            'name': 'Test Stage 3',
            'res_model': stage_model.id,
        })

        self.assertEqual(
            self.test_model._read_group_stage_ids(),
            (
                [(self.id_1, 'Test Stage 1'), (self.id_2, 'Test Stage 2')],
                {self.id_1: False, self.id_2: True},
            )
        )
