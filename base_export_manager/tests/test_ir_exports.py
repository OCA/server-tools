# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


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
