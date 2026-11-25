# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import base64
import json
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

from openpyxl import Workbook, load_workbook

from odoo.exceptions import UserError, ValidationError
from odoo.tests import mute_logger

from odoo.addons.excel_import_export.controllers.report import ReportExcelController
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
        """Import multiple contact lines through Odoo's real import service."""
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Sheet1"
        sheet["A1"] = "Álvaro"
        sheet["A2"] = "=literal"
        sheet["A2"].data_type = "s"
        content = BytesIO()
        workbook.save(content)
        record = self.env["xlsx.import"]._import_record_data(
            base64.b64encode(content.getvalue()),
            self.partner,
            {"Sheet1": {"child_ids": {"A1": "name"}}},
        )
        self.assertEqual(record, self.partner)
        self.assertEqual(
            {child.name for child in record.child_ids}, {"Álvaro", "=literal"}
        )

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

    def test_18_intermediate_xlsx_content(self) -> None:
        """The intermediate XLSX keeps cell values and can be read by Odoo."""
        service = self.env["xlsx.import"]
        values = {
            "child_ids/name": ["Álvaro", "=literal", "#N/A"],
            "child_ids/ref": ["", 42, False],
        }
        data = {"Sheet1": {"_HEAD_": {"A1": "name"}, "child_ids": {"A1": "name"}}}
        with (
            patch.object(type(service), "_get_line_vals", return_value=values),
            patch.object(type(service), "_execute_import", return_value={}) as execute,
        ):
            service._import_record_data(self.dummy_xlsx_b64, self.partner, data)
        imported = execute.call_args.args[0]
        self.assertEqual(imported.file_name, "temp.xlsx")
        self.assertEqual(
            imported.file_type,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        sheet = load_workbook(BytesIO(imported.file), data_only=True)["Sheet 1"]
        xml_id = service.get_external_id(self.partner)
        self.assertEqual(
            list(sheet.values),
            [
                ("id", "name", "child_ids/name", "child_ids/ref"),
                (xml_id, False, "Álvaro", None),
                (None, None, "=literal", 42),
                (None, None, "#N/A", False),
            ],
        )
        _count, rows = imported._read_xlsx({})
        self.assertEqual(rows[2][2:], ["=literal", "42"])
        self.assertEqual(rows[3][2:], ["#N/A", "False"])

    def test_19_export_lines_styles_and_totals(self) -> None:
        """Export related records with styles and a spreadsheet total."""
        children = self.env["res.partner"].create(
            [
                {"name": "First contact", "parent_id": self.partner.id},
                {"name": "Second contact", "parent_id": self.partner.id},
            ]
        )
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Sheet1"
        self.env["xlsx.export"]._fill_workbook_data(
            workbook,
            self.partner,
            {
                "Sheet1": {
                    "_HEAD_": {"A1": "name#{font=bold}"},
                    "child_ids": {
                        "A2": "name#{fill=yellow}",
                        "B2": "id@{sum}",
                    },
                }
            },
        )
        self.assertEqual(sheet["A1"].value, self.partner.name)
        self.assertTrue(sheet["A1"].font.bold)
        self.assertEqual(
            [sheet["A2"].value, sheet["A3"].value], [child.name for child in children]
        )
        self.assertEqual([sheet["B2"].value, sheet["B3"].value], children.ids)
        self.assertEqual(sheet["B4"].value, "=sum(B2:B3)")
        self.assertEqual(sheet["A2"].fill.fgColor.rgb, "00FFFCB7")

    def test_20_import_action_lifecycle(self) -> None:
        """The contextual import action is created and removed for the template."""
        self.template.add_import_action()
        action = self.template.import_action_id
        self.assertEqual(action.res_model, "import.xlsx.wizard")
        self.assertEqual(action.binding_model_id.model, "res.partner")
        self.template.remove_import_action()
        self.assertFalse(action.exists())

    def test_21_template_selection_errors(self) -> None:
        """Both export and reporting wizards reject an empty template selection."""
        for model in ("export.xlsx.wizard", "xlsx.report", "import.xlsx.wizard"):
            with self.subTest(model=model), self.assertRaises(ValidationError):
                self.env[model].with_context(
                    template_domain=[("id", "=", 0)]
                ).default_get(["template_id"])

    def test_22_styles_validate_directives(self) -> None:
        """Style directives apply cell formatting and reject unknown options."""
        sheet = Workbook().active
        styles = self.env["xlsx.styles"].get_openpyxl_styles()
        cell = sheet["A1"]
        cell.value = 42
        common.fill_cell_style(
            cell, "font=bold;fill=red;align=center;style=number", styles
        )
        self.assertTrue(cell.font.bold)
        self.assertEqual(cell.fill.fgColor.rgb, "00FF0000")
        self.assertEqual(cell.alignment.horizontal, "center")
        self.assertEqual(cell.number_format, "#,##0.00")
        with mute_logger("odoo.tools.translate"):
            with self.assertRaises(ValidationError):
                common.fill_cell_style(cell, "unknown=red", styles)
            with self.assertRaises(ValidationError):
                common.fill_cell_style(cell, "font=unknown", styles)

    def test_23_export_wizard_download(self) -> None:
        """The export wizard stores the generated workbook for download."""
        wizard = (
            self.env["export.xlsx.wizard"]
            .with_context(
                active_model="res.partner",
                active_ids=[self.partner.id],
                template_domain=[("id", "=", self.template.id)],
            )
            .create(
                {
                    "template_id": self.template.id,
                    "res_model": "res.partner",
                    "res_ids": str(self.partner.id),
                }
            )
        )
        action = wizard.action_export()
        self.assertEqual(action["res_id"], wizard.id)
        self.assertEqual(wizard.state, "get")
        workbook = load_workbook(BytesIO(base64.b64decode(wizard.data)))
        self.assertEqual(workbook["Sheet1"]["A1"].value, self.partner.name)

    def test_24_export_rejects_missing_sheet_and_too_many_lines(self) -> None:
        """Invalid sheet names and exceeded line limits stop the export."""
        self.env["res.partner"].create(
            [
                {"name": "First", "parent_id": self.partner.id},
                {"name": "Second", "parent_id": self.partner.id},
            ]
        )
        service = self.env["xlsx.export"]
        workbook = Workbook()
        with mute_logger("odoo.tools.translate"), self.assertRaises(ValidationError):
            service._fill_workbook_data(workbook, self.partner, {"Missing": {}})
        with self.assertRaisesRegex(Exception, "exceed max records"):
            service._get_line_vals(self.partner, "child_ids[1]", ["name"])

    def test_25_import_cell_conversion(self) -> None:
        """Numeric and relational spreadsheet values retain their import meaning."""
        sheet = Workbook().active
        sheet["A1"] = "1,234.5"
        sheet["A2"] = "42.0"
        sheet["A3"] = 12
        sheet["A4"] = False
        sheet["A5"] = "not a number"
        self.assertEqual(common._get_cell_value(sheet["A1"], "float"), 1234.5)
        self.assertEqual(common._get_cell_value(sheet["A2"], "integer"), 42)
        self.assertEqual(common._get_cell_value(sheet["A3"], "many2one"), "12")
        self.assertIs(common._get_cell_value(sheet["A4"], "boolean"), False)
        self.assertEqual(common._get_cell_value(sheet["A5"], "integer"), "not a number")

    def test_26_spreadsheet_number_conversion(self) -> None:
        """Spreadsheet exports convert numbers, dates, and ordinary text."""
        self.assertEqual(common.str_to_number("42"), 42)
        self.assertEqual(common.str_to_number("12.5"), 12.5)
        self.assertEqual(common.str_to_number("001.5"), "001.5")
        self.assertEqual(common.str_to_number("two words"), "two words")
        self.assertEqual(
            common.str_to_number("2026-01-02").date().isoformat(), "2026-01-02"
        )

    def test_27_excel_report_requires_matching_template(self) -> None:
        """An Excel report cannot render without a matching template."""
        action = self.env["ir.actions.report"].create(
            {
                "name": "Missing Excel template",
                "model": "res.partner",
                "report_name": "missing-template.xlsx",
                "report_file": "missing-template.xlsx",
                "report_type": "excel",
            }
        )
        with self.assertRaises(UserError):
            action._render_excel([self.partner.id], {})

    def test_28_excel_report_response(self) -> None:
        """The Excel report route returns an XLSX with the configured filename."""
        self.env["ir.actions.report"].create(
            {
                "name": "Partner Excel",
                "model": "res.partner",
                "report_name": self.template.fname,
                "report_file": self.template.fname,
                "report_type": "excel",
                "print_report_name": "'partner-report'",
            }
        )
        fake_request = SimpleNamespace(
            env=self.env, make_response=lambda content, headers: (content, headers)
        )
        with patch(
            "odoo.addons.excel_import_export.controllers.report.request", fake_request
        ):
            content, headers = ReportExcelController.report_routes.original_endpoint(
                ReportExcelController(),
                self.template.fname,
                str(self.partner.id),
                "excel",
                context="{}",
                options="{}",
            )
        self.assertEqual(
            load_workbook(BytesIO(content))["Sheet1"]["A1"].value, self.partner.name
        )
        self.assertIn("partner-report.xlsx", dict(headers)["Content-Disposition"])

    def test_29_excel_report_download_routes(self) -> None:
        """The report download forwards record IDs and merged report context."""
        controller = ReportExcelController()
        with patch.object(
            ReportExcelController, "report_routes", return_value="ok"
        ) as route:
            result = ReportExcelController.report_download.original_endpoint(
                controller,
                json.dumps(["/report/excel/partner.report/12", "excel"]),
                context='{"lang": "en_US"}',
            )
            self.assertEqual(result, "ok")
            self.assertEqual(route.call_args.kwargs["docids"], "12")
            result = ReportExcelController.report_download.original_endpoint(
                controller,
                json.dumps(
                    [
                        "/report/excel/partner.report?context=%7B%22tz%22%3A%22UTC%22%7D",
                        "excel",
                    ]
                ),
                context='{"lang": "en_US"}',
            )
            self.assertEqual(result, "ok")
            self.assertEqual(
                json.loads(route.call_args.kwargs["context"]),
                {"lang": "en_US", "tz": "UTC"},
            )

    def test_30_import_wizard_context_validation(self) -> None:
        """An import action checks the requested values on its active record."""
        wizard = self.env["import.xlsx.wizard"]
        context = {
            "active_model": "res.partner",
            "active_id": self.partner.id,
            "template_context": {"name": self.partner.name},
        }
        self.assertIsNone(wizard.check_view_init(context))
        context["template_context"] = {"name": "another name"}
        with self.assertRaises(ValidationError):
            wizard.check_view_init(context)

    def test_31_import_post_operation(self) -> None:
        """A configured post-import operation receives the imported record."""
        self.env["xlsx.import"]._post_import_operation(
            self.partner, "${object.write(dict(ref='imported'))}"
        )
        self.assertEqual(self.partner.ref, "imported")
