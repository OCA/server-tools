# -*- coding: utf-8 -*-
# © 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestIrExportsLine(TransactionCase):

    def setUp(self):
        super(TestIrExportsLine, self).setUp()
        self.ir_export = self.env.ref('base_jsonify.ir_exp_partner')

    def test_alias_contrains(self):
        ir_export_lines_model = self.env['ir.exports.line']
        with self.assertRaises(ValidationError):
            # The field into the name must be also into the alias
            ir_export_lines_model.create({
                'export_id': self.ir_export.id,
                'name': 'name',
                'alias': 'toto:my_alias'
            })
        with self.assertRaises(ValidationError):
            # The hierarchy into the alias must be the same as the one into
            # the name
            ir_export_lines_model.create({
                'export_id': self.ir_export.id,
                'name': 'child_ids/child_ids/name',
                'alias': 'child_ids:children/name'
            })
        with self.assertRaises(ValidationError):
            # The hierarchy into the alias must be the same as the one into
            # the name and must contains the same fields as into the name
            ir_export_lines_model.create({
                'export_id': self.ir_export.id,
                'name': 'child_ids/child_ids/name',
                'alias': 'child_ids:children/category_id:category/name'
            })
        line = ir_export_lines_model.create({
            'export_id': self.ir_export.id,
            'name': 'child_ids/child_ids/name',
            'alias': 'child_ids:children/child_ids:children/name'
        })
        self.assertTrue(line)
