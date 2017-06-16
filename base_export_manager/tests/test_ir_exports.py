# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestIrExportsCase(TransactionCase):
    def test_create_with_basic_data(self):
        """Emulate creation from original form.

        This form is handled entirely client-side, and lacks some required
        field values.
        """
        # Emulate creation from JsonRpc, without model_id and field#_id
        data = {
            "name": u"Test éxport",
            "resource": "ir.exports",
            "export_fields": [
                [0, 0, {"name": "export_fields"}],
                [0, 0, {"name": "export_fields/create_uid"}],
                [0, 0, {"name": "export_fields/create_date"}],
                [0, 0, {"name": "export_fields/field1_id"}],
            ],
        }
        record = self.env["ir.exports"].create(data)

        self.assertEqual(record.model_id.model, data["resource"])

    def test_create_without_model(self):
        """Creating a record without ``model_id`` and ``resource`` fails."""
        IrExports = self.env["ir.exports"]
        model = IrExports._get_model_id("res.partner")

        # Creating with resource
        record = IrExports.create({
            "name": "some",
            "resource": model.model,
        })
        self.assertEqual(record.model_id, model)

        # Creating with model_id
        record = IrExports.create({
            "name": "some",
            "model_id": model.id,
        })
        self.assertEqual(record.resource, model.model)

        # Creating without anyone
        with self.assertRaises(ValidationError):
            IrExports.create({
                "name": "some",
            })
