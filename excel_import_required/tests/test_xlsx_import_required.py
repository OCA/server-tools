# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import io

import openpyxl

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestXLSXImportRequired(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Template = self.env["xlsx.template"]
        self.Import = self.env["xlsx.import"]

        # Create a test template for res.partner
        self.template = self.Template.create(
            {
                "name": "Test Partner Import",
                "res_model": "res.partner",
                "instruction": str(
                    {
                        "__IMPORT__": {
                            "Sheet1": {
                                "_HEAD_": {
                                    "A1": "name",
                                }
                            }
                        }
                    }
                ),
            }
        )

        # Add import instruction lines
        self.env["xlsx.template.import"].create(
            [
                {
                    "template_id": self.template.id,
                    "section_type": "sheet",
                    "sheet": "Sheet1",
                    "sequence": 1,
                },
                {
                    "template_id": self.template.id,
                    "section_type": "head",
                    "row_field": "_HEAD_",
                    "sequence": 2,
                },
                {
                    "template_id": self.template.id,
                    "section_type": "data",
                    "excel_cell": "A1",
                    "field_name": "name",
                    "required": True,
                    "sequence": 3,
                },
            ]
        )

    def _create_excel_file(self, data):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        for row_idx, row_data in enumerate(data, start=1):
            for col_idx, cell_value in enumerate(row_data, start=1):
                ws.cell(row=row_idx, column=col_idx, value=cell_value)

        fp = io.BytesIO()
        wb.save(fp)
        return base64.b64encode(fp.getvalue())

    def test_01_import_required_field_missing(self):
        """Test that importing with a missing required field raises ValidationError."""
        # Create Excel file with empty A1 (Required field 'name')
        excel_file = self._create_excel_file([[""]])

        with self.assertRaises(ValidationError) as e:
            self.Import.import_xlsx(excel_file, self.template)

        self.assertIn("Following fields are required to import", e.exception.args[0])
        self.assertIn("Name", e.exception.args[0])

    def test_02_import_required_field_present(self):
        """Test that importing with a required field present does not raise."""
        excel_file = self._create_excel_file([["Test Partner"]])

        # Should not raise ValidationError when required field has data
        try:
            self.Import.import_xlsx(excel_file, self.template)
        except ValidationError:
            self.fail("ValidationError raised when required field was present")
