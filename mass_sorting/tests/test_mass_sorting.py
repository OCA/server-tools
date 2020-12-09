# Copyright 2021 Initos Gmbh
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMassSorting(TransactionCase):

    def setUp(self):
        super(TestMassSorting, self).setUp()
        self.model_id = self.env.ref('mass_sorting.model_mass_sort_config')
        self.o2m_field_id = self.env.ref(
            'mass_sorting.field_mass_sort_config_line_ids')
        self.field_id = self.env.ref(
            'mass_sorting.field_mass_sort_config_line_desc')
        self.config_id = self.env['mass.sort.config'].create({
            'name': 'Mass Sorting Test',
            'model_id': self.env.ref('mass_sorting.model_mass_sort_config').id,
            'one2many_field_id': self.o2m_field_id.id,
        })
        self.config_without_line_id = self.env['mass.sort.config'].create({
            'name': 'Test Mass Sorting without line',
            'model_id': self.env.ref('mass_sorting.model_mass_sort_config').id,
            'one2many_field_id': self.o2m_field_id.id,
        })
        self.config_line_id = self.env['mass.sort.config.line'].create({
            'config_id': self.config_id.id,
            'field_id': self.field_id.id,
        })

    def test_mass_sorting_action(self):
        self.config_id.create_action()
        self.assertEqual(self.config_id.action_id.name,
                         'Mass Sort (%s)' % self.config_id.name)

    def test_mass_sort_config_model(self):
        model_id = self.env.ref('mass_sorting.model_mass_sort_wizard')
        with self.assertRaises(ValidationError):
            self.env['mass.sort.config'].create({
                'name': 'Mass Sorting Test',
                'model_id': model_id.id,
                'one2many_field_id': self.o2m_field_id.id,
            })

    def test_mass_sort_config_sequence(self):
        model_id = self.env.ref('base.model_res_partner')
        o2m_field_id = self.env.ref('base.field_res_partner_child_ids')
        with self.assertRaises(ValidationError):
            self.env['mass.sort.config'].create({
                'name': 'Mass Sorting Test',
                'model_id': model_id.id,
                'one2many_field_id': o2m_field_id.id,
            })

    def test_mass_sorting_config_line_field_model(self):
        with self.assertRaises(ValidationError):
            self.env['mass.sort.config.line'].create({
                'config_id': self.config_id.id,
                'field_id': self.o2m_field_id.id,
            })

    def test_mass_sorting_config_copy(self):
        self.config_copy_id = self.config_id.copy()
        self.assertEqual(self.config_copy_id.name,
                         '%s (copy)' % self.config_id.name)

    def test_mass_sorting_wizard(self):
        self.config_id.create_action()
        wizard_obj = self.env['mass.sort.wizard'].with_context(
            {'mass_sort_config_id': self.config_id.id})
        config_id = wizard_obj._default_config_id()
        line_ids = wizard_obj._default_line_ids()
        wiz_rec = wizard_obj.create({
            'config_id': config_id,
            'line_ids': line_ids
        })
        wiz_rec.button_apply()
        self.assertEqual(wiz_rec.line_ids.sequence, 1)

    def test_mass_sorting_wizard_line(self):
        self.config_without_line_id.create_action()
        wizard_obj = self.env['mass.sort.wizard'].with_context(
            {'mass_sort_config_id': self.config_without_line_id.id})
        with self.assertRaises(ValidationError):
            wizard_obj.create({
                'config_id': self.config_without_line_id.id,
            })
