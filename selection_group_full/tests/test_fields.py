# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from . import common


class TestGroupFullField(common.BaseTestGroupFull):

    @classmethod
    def setUpClass(cls):
        super(TestGroupFullField, cls).setUpClass()
        cls.selection_group_full_test_model_inst = \
            cls.env['selection.group.full.test.model'].create({'name': 'Test'})

    def test_selection_exists(self):
        self.assertEquals('selection.group.full.test.model',
                          self.group_full_test_model._name)
        self.assertEquals(['in_progress'],
                          self.group_full_test_model.state.group_full)

        read_group_result = [{'state': (u'new', 'New'), 'state_count': 1L,
                              '__domain': [(u'state', '=', u'new')]}]

        result = self.selection_group_full_test_model_inst.\
            _read_group_fill_results([], 'state', [], [], 'state_count',
                                     read_group_result, 'state')

        self.assertEquals(2, len(result))

        self.assertIn({'state': ((u'new', 'New'), None), 'state_count': 1L,
                       '__domain': [(u'state', '=', u'new')]}, result)
        self.assertIn({'count': 0, 'state': (('in_progress', 'In Progress'),
                                             None),
                       'domain': [('state', '=', 'in_progress')]}, result)
