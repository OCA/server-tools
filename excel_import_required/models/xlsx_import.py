# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import ValidationError

from odoo.addons.excel_import_export.models import common as co


class XLSXImport(models.AbstractModel):
    _inherit = "xlsx.import"

    @api.model
    def import_xlsx(self, import_file, template, res_model=False, res_id=False):
        required_cells = {}
        current_sheet = None
        current_row_field = None

        for line in template.import_ids:
            if line.section_type == "sheet":
                current_sheet = (
                    int(line.sheet) if str(line.sheet).isdigit() else line.sheet
                )

            elif line.section_type in ("head", "row"):
                current_row_field = line.row_field
                if line.section_type == "row" and line.no_delete:
                    current_row_field = f"_NODEL_{current_row_field}"

            elif line.section_type == "data" and line.required:
                required_cells.setdefault(current_sheet, {}).setdefault(
                    current_row_field, set()
                ).add(line.excel_cell)

        return super(
            XLSXImport,
            self.with_context(
                excel_required_cells=required_cells,
                excel_import_errors=[],
            ),
        ).import_xlsx(import_file, template, res_model=res_model, res_id=res_id)

    @api.model
    def _process_worksheet(
        self, wb, out_st, model, data_dict, header_fields, is_xlsx=False
    ):
        required_cells = self.env.context.get("excel_required_cells")
        errors = self.env.context.get("excel_import_errors")

        if not required_cells:
            return super()._process_worksheet(
                wb, out_st, model, data_dict, header_fields, is_xlsx=is_xlsx
            )
        self._validate_header_fields(
            wb, model, data_dict, required_cells, errors, is_xlsx
        )

        res = super()._process_worksheet(
            wb, out_st, model, data_dict, header_fields, is_xlsx=is_xlsx
        )

        if errors:
            raise ValidationError(self._format_errors(errors))
        return res

    def _validate_header_fields(
        self, wb, model, data_dict, required_cells, errors, is_xlsx
    ):
        for sheet_name, worksheet in data_dict.items():
            req_cells = required_cells.get(sheet_name, {}).get("_HEAD_")
            if not req_cells:
                continue

            sheet = self._get_sheet(wb, sheet_name, is_xlsx)
            if not sheet:
                continue

            for rc, field in worksheet.get("_HEAD_", {}).items():
                rc_pos, _ = co.get_field_condition(rc)
                if rc_pos not in req_cells:
                    continue
                field_name, _ = co.get_field_condition(field)
                value = self._read_cell(sheet, rc_pos, model, field_name, is_xlsx)

                if not value:
                    errors.append(self._get_field_string(model, field_name))

    @api.model
    def _get_line_vals(self, st, worksheet, model, line_field, is_xlsx=False):
        vals = super()._get_line_vals(st, worksheet, model, line_field, is_xlsx=is_xlsx)

        required_cells = self.env.context.get("excel_required_cells")
        errors = self.env.context.get("excel_import_errors")
        if not required_cells or errors is None:
            return vals

        req_cells = set()
        for sheet in required_cells.values():
            req_cells |= sheet.get(line_field, set())

        if not req_cells:
            return vals

        for rc, columns in worksheet.get(line_field, {}).items():
            rc_pos, _ = co.get_field_condition(rc)

            if rc_pos not in req_cells:
                continue
            columns = columns if isinstance(columns, list) else [columns]
            for field in columns:
                field_name, _ = co.get_field_condition(field)
                new_line_field, _ = co.get_line_max(line_field)
                out_field = f"{new_line_field}/{field_name}"

                values = vals.get(out_field, [])
                if not values or any(not v for v in values):
                    errors.append(self._get_field_string(model, out_field))
        return vals

    def _read_cell(self, sheet, rc_pos, model, field_name, is_xlsx):
        try:
            row, col = co.pos2idx(rc_pos)
            cell = (
                sheet.cell(row=row + 1, column=col + 1)
                if is_xlsx
                else sheet.cell(row, col)
            )
            field_type = self._get_field_type(model, field_name)
            return co._get_cell_value(cell, field_type=field_type)
        except Exception:
            return False

    def _get_sheet(self, wb, sheet_name, is_xlsx):
        try:
            if isinstance(sheet_name, str):
                return (
                    wb[sheet_name]
                    if is_xlsx
                    else co.xlrd_get_sheet_by_name(wb, sheet_name)
                )
            return (
                wb.worksheets[sheet_name - 1]
                if is_xlsx
                else wb.sheet_by_index(sheet_name - 1)
            )
        except Exception:
            return None

    def _get_field_string(self, model, field_path):
        try:
            record = self.env[model].new()
            field = None
            for f in field_path.split("/"):
                f_name = f.split(".")[0]
                field = record._fields.get(f_name)
                if not field:
                    return field_path
                if field.type in ("one2many", "many2many", "many2one"):
                    record = record[f_name]
            return field.string if field else field_path
        except Exception:
            return field_path

    def _format_errors(self, errors):
        unique_errors = sorted(set(errors))
        msg = self.env._("Following fields are required to import\n")
        return msg + "\n".join(f"- {e}" for e in unique_errors)
