# Copyright 2022 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Test both traditional (xls) as modern (xlsx) excel files."""
import unittest

from odoo.modules.module import get_module_resource
from odoo.tests.common import TransactionCase, can_import

ID_FIELD = {
    "id": "id",
    "name": "id",
    "string": "External ID",
    "required": False,
    "fields": [],
    "type": "id",
}
XLS_MIME_TYPE = "application/vnd.ms-excel"
XLSX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_test_content(filename):
    """Get test content from file in test_files directory."""
    xls_file_path = get_module_resource("base_import_xlsx", "test_files", filename)
    return open(xls_file_path, "rb").read()


class TestPreview(TransactionCase):
    """Test both traditional (xls) as modern (xlsx) excel files."""

    @unittest.skipUnless(can_import("xlrd"), "XLRD module not available")
    def test_xls_success(self):
        """Test old style xls file."""
        file_content = get_test_content("test.xls")
        import_wizard = self.env["base_import.import"].create(
            {
                "res_model": "base_import.tests.models.preview.excel",
                "file": file_content,
                "file_type": XLS_MIME_TYPE,
            }
        )
        self._check_excel_wizard(import_wizard)

    @unittest.skipUnless(can_import("openpyxl"), "openpyxl not available")
    def test_xlsx_success(self):
        """Test modern style xlsx file."""
        file_content = get_test_content("test.xlsx")
        import_wizard = self.env["base_import.import"].create(
            {
                "res_model": "base_import.tests.models.preview.excel",
                "file": file_content,
                "file_type": XLSX_MIME_TYPE,
            }
        )
        self._check_excel_wizard(import_wizard)

    def _check_excel_wizard(self, import_wizard):
        """Check result for either xls or alsx file."""
        result = import_wizard.parse_preview({"headers": True})
        self.assertIsNone(result.get("error"))
        self.assertEqual(
            result["matches"],
            {
                0: ["name"],
                1: ["somevalue"],
                2: ["counter"],
                3: ["date"],
                4: ["time"],
                5: ["amount"],
            },
        )
        self.assertEqual(
            result["headers"],
            ["name", "Some Value", "Counter", "Date", "Time", "Amount"],
        )
        self.assertItemsEqual(
            result["fields"],
            [
                ID_FIELD,
                {
                    "id": "name",
                    "name": "name",
                    "string": "Name",
                    "required": False,
                    "fields": [],
                    "type": "char",
                },
                {
                    "id": "somevalue",
                    "name": "somevalue",
                    "string": "Some Value",
                    "required": True,
                    "fields": [],
                    "type": "integer",
                },
                {
                    "id": "othervalue",
                    "name": "othervalue",
                    "string": "Other Variable",
                    "required": False,
                    "fields": [],
                    "type": "integer",
                },
                {
                    "id": "counter",
                    "name": "counter",
                    "string": "Counter",
                    "required": False,
                    "fields": [],
                    "type": "integer",
                },
                {
                    "id": "date",
                    "name": "date",
                    "string": "Date",
                    "required": False,
                    "fields": [],
                    "type": "date",
                },
                {
                    "id": "time",
                    "name": "time",
                    "string": "Time",
                    "required": False,
                    "fields": [],
                    "type": "datetime",
                },
                {
                    "id": "amount",
                    "name": "amount",
                    "string": "Amount",
                    "required": False,
                    "fields": [],
                    "type": "float",
                },
            ],
        )
        self.assertEqual(
            result["preview"],
            [
                ["foo", "1", "2", "2022-02-24", "2022-02-24 12:23:24", ""],
                ["bar", "3", "", "", "", "12.25"],
                ["qux", "5", "6", "1962-05-21", "1962-05-21 08:25:26", "65.43"],
            ],
        )
