# -*- coding: utf-8 -*-
import os
from . import common as co
from openpyxl.utils.exceptions import IllegalCharacterError
from openpyxl import load_workbook
import base64
from io import BytesIO
import time
from datetime import date, datetime as dt
from odoo.tools.float_utils import float_compare
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class XLSXExport(models.AbstractModel):
    _name = 'xlsx.export'

    @api.model
    def get_eval_context(self, model, record, value):
        eval_context = {'float_compare': float_compare,
                        'time': time,
                        'datetime': dt,
                        'date': date,
                        'value': value,
                        'object': record,
                        'model': self.env[model],
                        'env': self.env,
                        'context': self._context,
                        }
        return eval_context

    @api.model
    def _get_line_vals(self, record, line_field, fields):
        """ Get values of this field from record set """
        line_field, max_row = co.get_line_max(line_field)
        lines = record[line_field]
        if max_row > 0 and len(lines) > max_row:
            raise Exception(
                _('Records in %s exceed max record allowed!') % line_field)
        vals = dict([(field, []) for field in fields])
        # Get field condition & aggre function
        field_cond_dict = {}
        aggre_func_dict = {}
        field_format_dict = {}
        pair_fields = []  # I.e., ('debit${value and . or .}@{sum}', 'debit')
        for field in fields:
            temp_field, eval_cond = co.get_field_condition(field)
            temp_field, field_format = co.get_field_format(temp_field)
            raw_field, aggre_func = co.get_field_aggregation(temp_field)
            # Dict of all special conditions
            field_cond_dict.update({field: eval_cond})
            aggre_func_dict.update({field: aggre_func})
            field_format_dict.update({field: field_format})
            # --
            pair_fields.append((field, raw_field))
        # --
        for line in lines:
            for field in pair_fields:  # (field, raw_field)
                value = self._get_field_data(field[1], line)
                # Case Eval
                eval_cond = field_cond_dict[field[0]]
                if eval_cond:  # Get eval_cond of a raw field
                    eval_context = self.get_eval_context(record._name,
                                                         line, value)
                    # value = str(eval(eval_cond, eval_context))
                    # Test removing str(), coz some case, need resulting number
                    value = eval(eval_cond, eval_context)
                # --
                vals[field[0]].append(value)
        return (vals, aggre_func_dict, field_format_dict)

    @api.model
    def _fill_workbook_data(self, workbook, record, data_dict):
        """ Fill data from record with format in data_dict to workbook """
        if not record or not data_dict:
            return
        try:
            # variable to store data range of each worksheet
            worksheet_range = {}
            for sheet_name in data_dict:
                ws = data_dict[sheet_name]
                st = False
                if isinstance(sheet_name, str):
                    st = co.openpyxl_get_sheet_by_name(workbook, sheet_name)
                elif isinstance(sheet_name, int):
                    st = workbook.worksheets[sheet_name - 1]
                if not st:
                    raise ValidationError(
                        _('Sheet %s not found!') % sheet_name)
                # ================ HEAD ================
                self._fill_head(ws, st, record)
                # ============= Line Items =============
                # Check for groupby directive
                groupbys = {key: ws[key] for key in
                            filter(lambda l: l[0:9] == '_GROUPBY_', ws.keys())}
                all_rc, max_row, tail_fields = self._fill_lines(ws, st, record,
                                                                groupbys)
                # ================ TAIL ================
                self._fill_tail(ws, st, record, tail_fields)

                # prepare worksheet data range, to be used in BI funtions
                if all_rc:
                    begin_rc = min(all_rc)
                    col, row = co.split_row_col(
                        max(sorted(all_rc, reverse=True), key=len))
                    end_rc = '%s%s' % (col, max_row)
                    worksheet_range[sheet_name] = '%s:%s' % (begin_rc, end_rc)

        except KeyError as e:
            raise ValidationError(_('Key Error!\n%s') % e)
        except IllegalCharacterError as e:
            raise ValidationError(
                _('IllegalCharacterError!\n'
                  'Some exporting data contains special character\n%s') % e)
        except Exception as e:
            raise ValidationError(
                _('Error filling data into excel sheets!\n%s') % e)

    @api.model
    def _get_field_data(self, _field, _line):
        """ Get field data, and convert data type if needed """
        if not _field:
            return None
        line_copy = _line
        for f in _field.split('.'):
            data_type = line_copy._fields[f].type
            line_copy = line_copy[f]
            if data_type == 'date':
                if line_copy:
                    line_copy = dt.strptime(line_copy, '%Y-%m-%d')
            elif data_type == 'datetime':
                if line_copy:
                    line_copy = dt.strptime(line_copy, '%Y-%m-%d %H:%M:%S')
        if isinstance(line_copy, str):
            line_copy = line_copy.encode('utf-8')
        return line_copy

    @api.model
    def _fill_head(self, ws, st, record):
        for rc, field in ws.get('_HEAD_', {}).items():
            tmp_field, eval_cond = co.get_field_condition(field)
            tmp_field, field_format = co.get_field_format(tmp_field)
            value = tmp_field and self._get_field_data(tmp_field, record)
            # Case Eval
            if eval_cond:  # Get eval_cond of a raw field
                eval_context = self.get_eval_context(record._name,
                                                     record, value)
                # str() throw cordinal not in range error
                value = eval(eval_cond, eval_context)
                # value = str(eval(eval_cond, eval_context))
            if value is not None:
                st[rc] = value
            if field_format:
                co.fill_cell_format(st[rc], field_format)

    @api.model
    def _fill_lines(self, ws, st, record, groupbys):
        all_rc = []
        max_row = 0

        line_fields = list(ws)
        for x in ('_HEAD_', '_TAIL_', '_GROUPBY_'):
            for line_field in line_fields:
                if x in line_field:
                    line_fields.remove(line_field)
        tail_fields = {}  # Keep tail cell, to be used in _TAIL_
        for line_field in line_fields:

            subtotals = {'rows': [], 'subtotals': {},
                         'grandtotals': {}, 'formats': {}}
            # ====== GROUP BY =========
            groupby_keys = list(filter(lambda l: '_GROUPBY_%s' %
                                       line_field in l,  groupbys.keys()))
            if groupby_keys:
                groupby = co.get_groupby(groupby_keys[0])
                groupby_dict = groupbys[groupby_keys[0]]
                # If value in groupby changes, mark the row index
                i = 0
                old_val = []
                for line in record[line_field]:
                    val = []
                    for key in groupby:
                        val.append(line[key])
                    if i > 0 and val != old_val:
                        subtotals['rows'].append(i)
                    old_val = val
                    i += 1
                subtotals['rows'].append(i)
                # For the aggregrate column
                for cell in groupby_dict.keys():
                    col, row = co.split_row_col(cell)
                    first_row = row
                    cell_format = groupby_dict[cell]
                    _, grp_func = co.get_field_aggregation(cell_format)
                    _, grp_format = co.get_field_format(cell_format)

                    cell_field = ws[line_field][cell]
                    subtotals['subtotals'].update({cell_field: []})
                    subtotals['formats'].update({cell_field: []})
                    grandtotals = []
                    if subtotals['rows']:
                        subtotals['formats'][cell_field] = grp_format
                    for i in subtotals['rows']:
                        from_cell = '%s%s' % (col, row)
                        to_cell = '%s%s' % (col, first_row+i-1)
                        range_cell = '%s:%s' % (from_cell, to_cell)
                        subtotals['subtotals'][cell_field].append(
                            grp_func and
                            '=%s(%s)' % (grp_func, range_cell) or
                            '')
                        grandtotals.append(range_cell)
                        first_row += 1
                        row = first_row + i
                    if grandtotals:
                        subtotals['grandtotals'][cell_field] = \
                            '=%s(%s)' % (grp_func, ','.join(grandtotals))
                # --

            sb_rows = [i + v for i, v in enumerate(subtotals.get('rows', []))]
            sb_subtotals = subtotals.get('subtotals', {})
            sb_grandtotals = subtotals.get('grandtotals', {})
            sb_formats = subtotals.get('formats', {})

            fields = ws.get(line_field, {}).values()
            all_rc += ws.get(line_field, {}).keys()
            (vals, func, field_format) = \
                self._get_line_vals(record, line_field, fields)
            # value with '\\skiprow' signify line skipping
            vals = co.add_row_skips(vals)

            for rc, field in ws.get(line_field, {}).items():
                tail_fields[rc] = False
                col, row = co.split_row_col(rc)  # starting point
                i = 0
                new_row = 0
                new_rc = rc
                for val in vals[field]:
                    row_vals = isinstance(val, str) and \
                        val.split('\\skiprow') or [val]
                    for row_val in row_vals:
                        new_row = row + i
                        new_rc = '%s%s' % (col, new_row)
                        row_val = co.adjust_cell_formula(row_val, i)
                        if row_val not in ('None', None):
                            st[new_rc] = co.str_to_number(row_val)
                        if field_format.get(field, False):
                            co.fill_cell_format(st[new_rc],
                                                field_format[field])
                        # ====== GROUP BY =========
                        # Sub Total
                        for j in sb_rows:
                            if i == j-1:
                                new_row = row + i
                                if sb_subtotals.get(field, False):
                                    new_rc = '%s%s' % (col, new_row + 1)
                                    row_val = sb_subtotals[field][0]
                                    st[new_rc] = co.str_to_number(row_val)
                                    sb_subtotals[field].pop(0)
                                if sb_formats.get(field, False):
                                    new_rc = '%s%s' % (col, new_row + 1)
                                    grp_format = sb_formats[field]
                                    if grp_format:
                                        co.fill_cell_format(st[new_rc],
                                                            grp_format)
                                i += 1
                        # ---------------------------
                        if new_row > max_row:
                            max_row = new_row
                        i += 1

                # Grand Total
                if sb_grandtotals.get(field, False):
                    new_rc = '%s%s' % (col, new_row + 2)
                    row_val = sb_grandtotals[field]
                    st[new_rc] = co.str_to_number(row_val)
                if sb_formats.get(field, False):
                    new_rc = '%s%s' % (col, new_row + 2)
                    grp_format = sb_formats[field]
                    if grp_format:
                        co.fill_cell_format(st[new_rc], grp_format)

                # Add footer line if at least one field have func
                f = func.get(field, False)
                if f:
                    new_row += 1
                    f_rc = '%s%s' % (col, new_row)
                    st[f_rc] = '=%s(%s:%s)' % (f, rc, new_rc)

                tail_fields[rc] = new_rc   # Last row field

        return all_rc, max_row, tail_fields

    @api.model
    def _fill_tail(self, ws, st, record, tail_fields):
        # Get the max last rc's row
        last_row = 0
        for to_rc in tail_fields.values():
            _, row = co.split_row_col(to_rc)
            last_row = row > last_row and row or last_row
        # Similar to header, except it will set cell after last row
        # Get all tails, i.e., _TAIL_0, _TAIL_1 order by number
        tails = filter(lambda l: l[0:6] == '_TAIL_', ws.keys())
        tail_dicts = {key: ws[key] for key in tails}
        for tail_key, tail_dict in tail_dicts.items():
            row_skip = tail_key[6:] != '' and int(tail_key[6:]) or 0
            # For each _TAIL_ and row skipper 0, 1, 2, ...
            for rc, field in tail_dict.items():
                tmp_field, eval_cond = co.get_field_condition(field)
                tmp_field, field_format = co.get_field_format(tmp_field)
                tmp_field, func = co.get_field_aggregation(tmp_field)
                value = tmp_field and self._get_field_data(tmp_field, record)
                # Case Eval
                if eval_cond:  # Get eval_cond of a raw field
                    eval_context = self.get_eval_context(record._name,
                                                         record, value)
                    # str() throw cordinal not in range error
                    value = eval(eval_cond, eval_context)
                    # value = str(eval(eval_cond, eval_context))
                # If no rc in tail_fields, use the max last row
                last_rc = False
                tail_rc = False
                if rc in tail_fields.keys():
                    last_rc = tail_fields[rc]  # Last row of rc column
                    col, row = co.split_row_col(last_rc)
                    tail_rc = '%s%s' % (col, row + row_skip + 1)
                else:
                    col, _ = co.split_row_col(rc)
                    last_rc = '%s%s' % (col, last_row)
                    tail_rc = '%s%s' % (col, last_row + row_skip + 1)
                if value and value is not None:
                    st[tail_rc] = value
                if func:
                    st[tail_rc] = '=%s(%s:%s)' % (func, rc, last_rc)
                if field_format:
                    co.fill_cell_format(st[tail_rc], field_format)

    @api.model
    def export_xlsx(self, template, res_model, res_id):
        if template.res_model != res_model:
            raise ValidationError(_("Template's model mismatch"))
        data_dict = co.literal_eval(template.instruction.strip())
        export_dict = data_dict.get('__EXPORT__', False)
        out_name = template.name
        if not export_dict:  # If there is not __EXPORT__ formula, just export
            out_name = template.fname
            out_file = template.datas
            return (out_file, out_name)
        # Prepare temp file (from now, only xlsx file works for openpyxl)
        decoded_data = base64.decodestring(template.datas)
        ConfParam = self.env['ir.config_parameter']
        ptemp = ConfParam.get_param('path_temp_file') or '/tmp'
        stamp = dt.utcnow().strftime('%H%M%S%f')[:-3]
        ftemp = '%s/temp%s.xlsx' % (ptemp, stamp)
        f = open(ftemp, 'wb')
        f.write(decoded_data)
        f.seek(0)
        f.close()
        # Workbook created, temp fie removed
        wb = load_workbook(ftemp)
        os.remove(ftemp)
        # ============= Start working with workbook =============
        record = res_model and self.env[res_model].browse(res_id) or False
        self._fill_workbook_data(wb, record, export_dict)
        # =======================================================
        # Return file as .xlsx
        content = BytesIO()
        wb.save(content)
        content.seek(0)  # Set index to 0, and start reading
        out_file = base64.encodestring(content.read())
        if record and 'name' in record and record.name:
            out_name = record.name.replace(' ', '').replace('/', '')
        else:
            fname = out_name.replace(' ', '').replace('/', '')
            ts = fields.Datetime.context_timestamp(self, dt.now())
            out_name = '%s_%s' % (fname, ts.strftime('%Y%m%d_%H%M%S'))
        if not out_name or len(out_name) == 0:
            out_name = 'noname'
        out_ext = 'xlsx'
        # CSV (convert only 1st sheet)
        if template.to_csv:
            delimiter = template.csv_delimiter
            out_file = co.csv_from_excel(out_file, delimiter,
                                         template.csv_quote)
            out_ext = template.csv_extension
        return (out_file, '%s.%s' % (out_name, out_ext))
