# Copyright 2024 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAuditlogLogLine(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group_portal = cls.env.ref('base.group_portal')
        cls.group_user = cls.env.ref('base.group_user')

        cls.model = cls.env['ir.model'].create({
            'name': 'Test Model',
            'model': 'x_test_model',
        })

        cls.field = cls.env['ir.model.fields'].create({
            'name': 'x_test_field',
            'model_id': cls.model.id,
            'field_description': 'Test Field',
            'ttype': 'char',
        })

        cls.log = cls.env['auditlog.log'].create({
            'method': 'write',
            'model_id': cls.model.id,
            'res_id': 1,
        })

    def test_compute_method(self):
        """Test the computation of the method field"""

        log_line = self.env['auditlog.log.line'].create({
            'log_id': self.log.id,
            'field_id': self.field.id,
            'old_value': 'old',
            'new_value': 'new',
        })
        self.assertEqual(
            log_line.method,
            'write',
            "The computed method field is incorrect."
        )

    def test_compute_model_id(self):
        """Test the computation of the model_id field"""
        log_line = self.env['auditlog.log.line'].create({
            'log_id': self.log.id,
            'field_id': self.field.id,
            'old_value': 'old',
            'new_value': 'new',
        })
        self.assertEqual(
            log_line.model_id,
            self.model,
            "The computed model_id field is incorrect."
        )

    def test_compute_res_id(self):
        """Test the computation of the res_id field"""
        log_line = self.env['auditlog.log.line'].create({
            'log_id': self.log.id,
            'field_id': self.field.id,
            'old_value': 'old',
            'new_value': 'new',
        })
        self.assertEqual(
            log_line.res_id,
            1,
            "The computed res_id field is incorrect."
        )
