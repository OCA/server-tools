import base64
from unittest.mock import patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestExcelImportExport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Template = self.env["xlsx.template"]
        self.report_model = "my.custom.report"
        self.template_valid = self.Template.create(
            {
                "name": "Valid Template",
                "datas": "VGhpcyBpcyBhIHRlc3QgZGF0YQ==",
            }
        )
        self.template_valid_2 = self.Template.create(
            {
                "name": "Second Valid Template",
                "datas": "VGhpcyBpcyBhbm90aGVyIGRhdGE=",
            }
        )
        self.template_no_file = self.Template.create(
            {
                "name": "No File Template",
                "datas": False,
            }
        )
        self.ReportModel = self.env["xlsx.report"].with_context(
            template_domain=[
                ("id", "in", [self.template_valid.id, self.template_valid_2.id])
            ]
        )
        self.ReportAction = self.env["ir.actions.report"]
        self.report_action = self.ReportAction.create(
            {
                "name": "My Excel Report",
                "report_name": "my_report",
                "model": "res.partner",
                "report_type": "excel",
            }
        )
        self.xlsx_template = self.Template.create(
            {
                "name": "My Excel Template",
                "fname": "my_report",
                "res_model": "res.partner",
                "datas": base64.b64encode(b"FAKE DATA"),
            }
        )

    def test_t01_default_get_single_template(self):
        Report = self.ReportModel.with_context(
            template_domain=[("id", "=", self.template_valid.id)]
        )
        defaults = Report.default_get(Report._fields.keys())
        self.assertEqual(defaults.get("template_id"), self.template_valid.id)

    def test_t02_default_get_multiple_templates(self):
        defaults = self.ReportModel.default_get(self.ReportModel._fields.keys())
        self.assertFalse(defaults.get("template_id"))

    def test_t03_default_get_no_template_found(self):
        Report = self.ReportModel.with_context(template_domain=[("id", "=", 999)])
        with self.assertRaisesRegex(ValidationError, "No template found"):
            Report.default_get(Report._fields.keys())

    def test_t04_default_get_template_no_file(self):
        Report = self.ReportModel.with_context(
            template_domain=[("id", "=", self.template_no_file.id)]
        )
        with self.assertRaisesRegex(ValidationError, "No file in No File Template"):
            Report.default_get(Report._fields.keys())

    def test_t05_render_excel_multiple_docids(self):
        with self.assertRaises(UserError) as cm:
            self.report_action._render_excel([1, 2], {})
        self.assertIn("Only one id is allowed", str(cm.exception))

    def test_t06_render_excel_no_unique_template(self):
        self.xlsx_template.unlink()
        with self.assertRaises(UserError) as cm:
            self.report_action._render_excel([1], {})
        self.assertIn("is not unique", str(cm.exception))

    def test_t07_render_excel_success(self):
        fake_out_file = b"FAKE_XLSX"
        fake_out_name = "report.xlsx"

        with patch(
            "odoo.addons.excel_import_export.models.xlsx_export.XLSXExport.export_xlsx"
        ) as mock_export:
            mock_export.return_value = (fake_out_file, fake_out_name)

            out_file, out_name = self.report_action._render_excel([1], {})
            self.assertEqual(out_file, fake_out_file)
            self.assertEqual(out_name, fake_out_name)

            mock_export.assert_called_once_with(self.xlsx_template, "res.partner", 1)

    def test_t08_get_report_from_name(self):
        res = self.report_action._get_report_from_name("my_report")
        self.assertEqual(res, self.report_action)
