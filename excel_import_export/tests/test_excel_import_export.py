# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import base64

from odoo.exceptions import UserError, ValidationError

from odoo.addons.excel_import_export.models import common

from .common import TestExcelImportExportCommon


class TestExcelImportExport(TestExcelImportExportCommon):
    def test_01_compute_instructions_from_dict(self):
        """Test the string dictionary is parsed into the Odoo lines correctly"""
        self.assertTrue(self.template.export_ids)
        self.assertTrue(self.template.import_ids)
        export_data_lines = self.template.export_ids.filtered(
            lambda line: line.section_type == "data"
        )
        self.assertEqual(
            len(export_data_lines), 2, "It should parse 2 data fields for Export"
        )
        self.assertIn("name", export_data_lines.mapped("field_name"))

    def test_02_add_and_remove_export_action(self):
        """Test the creation and removal of contextual export actions"""
        self.template.add_export_action()
        self.assertTrue(self.template.export_action_id)
        self.assertEqual(self.template.export_action_id.res_model, "export.xlsx.wizard")
        self.assertEqual(
            self.template.export_action_id.binding_model_id.model, "res.partner"
        )
        self.template.remove_export_action()
        self.assertFalse(self.template.export_action_id)

    def test_03_easy_reporting_menu(self):
        """Test Easy Reporting Wizard capabilities"""
        self.template.write(
            {
                "use_report_wizard": True,
                "result_model_id": self.env["ir.model"]._get_id("res.partner"),
            }
        )
        self.assertTrue(self.template.result_field)
        self.assertEqual(self.template.res_model, "res.partner")
        self.template.add_report_menu()
        self.assertTrue(self.template.report_action_id)
        self.assertTrue(self.template.report_menu_id)
        self.template.remove_report_menu()
        self.assertFalse(self.template.report_action_id)
        self.assertFalse(self.template.report_menu_id)

    def test_04_export_wizard_default_get(self):
        """Test that the export wizard finds the right template based on context"""
        self.template.write(
            {
                "use_report_wizard": False,
                "res_model": "res.partner",
            }
        )
        self.template.add_export_action()
        Wizard = self.env["export.xlsx.wizard"].with_context(
            active_model="res.partner",
            active_ids=[self.partner.id],
            template_domain=[("res_model", "=", "res.partner")],
        )
        defaults = Wizard.default_get(["template_id", "res_ids", "res_model"])
        self.assertEqual(defaults.get("template_id"), self.template.id)
        self.assertEqual(defaults.get("res_model"), "res.partner")
        self.assertEqual(defaults.get("res_ids"), str(self.partner.id))

    def test_05_mismatch_model_exception(self):
        """Test that attempting to export with a wrong model raises ValidationError"""
        ExportService = self.env["xlsx.export"]
        with self.assertRaises(ValidationError):
            ExportService.export_xlsx(self.template, res_model="res.users", res_ids=[1])

    def test_06_actual_export(self):
        """Test standard export capabilities"""
        ExportService = self.env["xlsx.export"]
        out_file, out_name = ExportService.export_xlsx(
            self.template, res_model="res.partner", res_ids=[self.partner.id]
        )
        self.assertTrue(out_file)
        self.assertTrue(out_name)

    def test_07_export_multiple_records_zip(self):
        """Test exporting multiple records to force the ZIP fallback"""
        partner2 = self.env["res.partner"].create({"name": "Partner 2"})
        ExportService = self.env["xlsx.export"]
        out_file, out_name = ExportService.export_xlsx(
            self.template,
            res_model="res.partner",
            res_ids=[self.partner.id, partner2.id],
        )
        self.assertTrue(out_file)
        self.assertEqual(out_name, "files.zip")

    def test_08_actual_import(self):
        """Test standard import back from exported file"""
        ExportService = self.env["xlsx.export"]
        out_file, out_name = ExportService.export_xlsx(
            self.template, res_model="res.partner", res_ids=[self.partner.id]
        )
        ImportService = self.env["xlsx.import"]
        record = ImportService.import_xlsx(
            out_file, self.template, res_model="res.partner", res_id=False
        )
        self.assertTrue(record)

    def test_09_report_render_excel(self):
        """Test the report action override"""
        report_action = self.env["ir.actions.report"].create(
            {
                "name": "Test Excel Report",
                "model": "res.partner",
                "report_name": "test_partner.xlsx",
                "report_file": "test_partner.xlsx",
                "report_type": "excel",
            }
        )
        excel_data = report_action._render_excel([self.partner.id], {})
        self.assertTrue(excel_data)
        self.assertTrue(excel_data[1].endswith(".xlsx"))
        # Test error for multiple ids
        with self.assertRaises(UserError):
            report_action._render_excel([self.partner.id, self.partner.id], {})

    def test_10_common_utils(self):
        """Test coverage for common tools functions"""
        self.assertEqual(common.split_row_col("A1"), ("A", 1))
        self.assertEqual(common.pos2idx("A1"), (0, 0))
        self.assertEqual(common.pos2idx("B2"), (1, 1))
        self.assertTrue(common.isdatetime("2020-01-01"))
        self.assertTrue(common.isdatetime("2020-01-01 10:00:00"))
        self.assertFalse(common.isdatetime("abc"))
        self.assertTrue(common.isfloat("1.23"))
        self.assertFalse(common.isfloat("abc"))
        self.assertTrue(common.isinteger("123"))
        self.assertFalse(common.isinteger("abc"))
        self.assertEqual(common.adjust_cell_formula("?(A1)+?(B2)", 5), "A6+B7")
        self.assertEqual(common.get_field_aggregation("field@{sum}"), ("field", "sum"))
        self.assertEqual(
            common.get_field_style("field#{font=bold}"), ("field", "font=bold")
        )
        self.assertEqual(
            common.get_field_condition("field${value > 0}"), ("field", "value > 0")
        )
        self.assertEqual(
            common.get_groupby('line_ids["a_id", "b_id"]'), ["a_id", "b_id"]
        )

    def test_11_csv_export(self):
        """Test csv exportation override in template"""
        self.template.to_csv = True
        ExportService = self.env["xlsx.export"]
        out_file, out_name = ExportService.export_xlsx(
            self.template, res_model="res.partner", res_ids=[self.partner.id]
        )
        self.assertTrue(out_name.endswith(".csv"))

    def test_12_report_xlsx_wizard(self):
        """Test execution of the specific wizard view"""
        self.template.write(
            {
                "use_report_wizard": True,
                "result_model_id": self.env["ir.model"]._get_id("res.partner"),
            }
        )
        self.template.add_report_menu()
        action_id = self.template.report_action_id.id

        wizard = (
            self.env["report.xlsx.wizard"]
            .with_context(report_action_id=action_id)
            .create(
                {
                    "res_model": "res.partner",
                    "domain": "[]",
                }
            )
        )
        res = wizard.action_report()
        self.assertEqual(res["type"], "ir.actions.report")

    def test_13_import_wizard(self):
        """Test import wizard views and flow"""
        wizard = (
            self.env["import.xlsx.wizard"]
            .with_context(
                active_model="res.partner",
                active_id=self.partner.id,
                template_domain=[("id", "=", self.template.id)],
            )
            .create(
                {
                    "template_id": self.template.id,
                }
            )
        )
        sample = wizard.get_import_sample()
        self.assertEqual(sample["res_model"], "import.xlsx.wizard")

        ExportService = self.env["xlsx.export"]
        out_file, _ = ExportService.export_xlsx(
            self.template, res_model="res.partner", res_ids=[self.partner.id]
        )
        wizard.import_file = out_file
        wizard.action_import()
        self.assertEqual(wizard.state, "get")

    def test_14_xlsx_report_abstract_model(self):
        """Test default get on the base report model"""
        defaults = (
            self.env["xlsx.report"]
            .with_context(template_domain=[("id", "=", self.template.id)])
            .default_get(["template_id"])
        )
        self.assertEqual(defaults.get("template_id"), self.template.id)

    def test_15_styles(self):
        """Test the generic styler load"""
        styles = self.env["xlsx.styles"].get_openpyxl_styles()
        self.assertIn("font", styles)
        self.assertIn("fill", styles)
        self.assertIn("align", styles)

    def test_16_csv_from_excel_util(self):
        """Test CSV converter natively"""
        out_file, _ = self.env["xlsx.export"].export_xlsx(
            self.template, res_model="res.partner", res_ids=[self.partner.id]
        )
        excel_content = base64.b64decode(out_file)
        csv_content = common.csv_from_excel(excel_content, ",", True)
        self.assertTrue(csv_content)

    def test_17_get_field_type_deep(self):
        """Test deep model search for types in import utility."""
        field_type = self.env["xlsx.import"]._get_field_type(
            "res.partner", "child_ids/name"
        )
        self.assertEqual(field_type, "char")
