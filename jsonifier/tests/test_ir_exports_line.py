# Copyright 2017 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestIrExportsLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ir_export = cls.env.ref("jsonifier.ir_exp_partner")

    def test_target_constrains(self):
        ir_export_lines_model = self.env["ir.exports.line"]
        with self.assertRaises(ValidationError):
            # The field into the name must be also into the target
            ir_export_lines_model.create(
                {
                    "export_id": self.ir_export.id,
                    "name": "name",
                    "target": "toto:my_target",
                }
            )
        with self.assertRaises(ValidationError):
            # The hierarchy into the target must be the same as the one into
            # the name
            ir_export_lines_model.create(
                {
                    "export_id": self.ir_export.id,
                    "name": "child_ids/child_ids/name",
                    "target": "child_ids:children/name",
                }
            )
        with self.assertRaises(ValidationError):
            # The hierarchy into the target must be the same as the one into
            # the name and must contains the same fields as into the name
            ir_export_lines_model.create(
                {
                    "export_id": self.ir_export.id,
                    "name": "child_ids/child_ids/name",
                    "target": "child_ids:children/category_id:category/name",
                }
            )
        line = ir_export_lines_model.create(
            {
                "export_id": self.ir_export.id,
                "name": "child_ids/child_ids/name",
                "target": "child_ids:children/child_ids:children/name",
            }
        )
        self.assertTrue(line)

    def test_resolver_function_constrains(self):
        resolver = self.env["ir.exports.resolver"].create(
            {"python_code": "result = value", "type": "field"}
        )
        ir_export_lines_model = self.env["ir.exports.line"]
        with self.assertRaises(ValidationError):
            # the callable should be an existing model function, but it's not checked
            ir_export_lines_model.create(
                {
                    "export_id": self.ir_export.id,
                    "name": "name",
                    "resolver_id": resolver.id,
                    "instance_method_name": "function_name",
                }
            )
