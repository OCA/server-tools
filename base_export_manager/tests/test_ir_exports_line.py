# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class TestIrExportsLineCase(TransactionCase):
    def setUp(self):
        super(TestIrExportsLineCase, self).setUp()
        m_ir_exports = self.env['ir.exports']
        self.export = m_ir_exports.create({'name': 'Partner Test',
                                           'resource': 'res.partner'})
        self.partner_model = self.env['ir.model'].search(
            [('model', '=', 'res.partner')])
        self.field_parent_id = self.env['ir.model.fields'].search(
            [('name', '=', 'parent_id'),
             ('model_id', '=', self.partner_model.id)])
        self.field_name = self.env['ir.model.fields'].search(
            [('name', '=', 'name'),
             ('model_id', '=', self.partner_model.id)])

    def test_check_name(self):
        m_ir_exports_line = self.env['ir.exports.line']
        m_ir_exports_line.create({'name': 'name',
                                  'export_id': self.export.id})
        with self.assertRaises(ValidationError):
            m_ir_exports_line.create({'name': 'name',
                                      'export_id': self.export.id})
        with self.assertRaises(ValidationError):
            m_ir_exports_line.create({'name': 'bad_error_name',
                                      'export_id': self.export.id})

    def test_get_label_string(self):
        m_ir_exports_line = self.env['ir.exports.line']
        export_line = m_ir_exports_line.create({'name': 'parent_id/name',
                                                'export_id': self.export.id})
        self.assertEqual(export_line.with_context(lang="en_US").label,
                         "Related Company/Name (parent_id/name)")
        with self.assertRaises(ValidationError):
            m_ir_exports_line.create({'name': '',
                                      'export_id': self.export.id})

    def test_model_default_by_context(self):
        """Fields inherit the model_id by context."""
        line = self.env["ir.exports.line"].with_context(
            default_model1_id=self.export.model_id.id).create({
                "name": "name",
                "export_id": self.export.id,
            })
        self.assertEqual(line.model1_id, self.export.model_id)

    def test_inverse_name(self):
        line = self.env['ir.exports.line'].create({
            'export_id': self.export.id,
            'name': 'parent_id/parent_id/parent_id/name',
        })
        self.assertEqual(line.model1_id, self.partner_model)
        self.assertEqual(line.model2_id, self.partner_model)
        self.assertEqual(line.field1_id, self.field_parent_id)
        self.assertEqual(line.field2_id, self.field_parent_id)
        self.assertEqual(line.field3_id, self.field_parent_id)
        self.assertEqual(line.field4_id, self.field_name)

    def test_compute_name(self):
        line = self.env['ir.exports.line'].create({
            'export_id': self.export.id,
            'field1_id': self.field_parent_id.id,
            'field2_id': self.field_parent_id.id,
            'field3_id': self.field_parent_id.id,
            'field4_id': self.field_name.id,
        })
        self.assertEqual(line.name, 'parent_id/parent_id/parent_id/name')

    def test_write_name_same_root(self):
        self.env['ir.exports.line'].create({
            'export_id': self.export.id,
            'name': 'parent_id',
        })
        line = self.env['ir.exports.line'].create({
            'export_id': self.export.id,
            'name': 'name',
        })
        # This should end without errors
        line.name = 'parent_id/name'
