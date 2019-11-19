# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import os
import logging
import base64
from io import BytesIO
import time
from datetime import date, datetime as dt
from odoo.tools.float_utils import float_compare
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError
from . import common as co

_logger = logging.getLogger(__name__)
try:
    from openpyxl import load_workbook
    from openpyxl.utils.exceptions import IllegalCharacterError
except ImportError:
    _logger.debug(
        'Cannot import "openpyxl". Please make sure it is installed.')


class XLSXExport(models.AbstractModel):
    _name = 'xlsx.export'
    _description = 'Excel Export AbstractModel'

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
        """ Get values of this field from record set and return as dict of vals
            - record: main object
            - line_field: rows object, i.e., line_ids
            - fields: fields in line_ids, i.e., partner_id.display_name
        """
        line_field, max_row = co.get_line_max(line_field)
        line_field = line_field.replace('_CONT_', '')  # Remove _CONT_ if any
        lines = record[line_field]
        if max_row > 0 and len(lines) > max_row:
            raise Exception(
                _('Records in %s exceed max records allowed') % line_field)
        vals = dict([(field, []) for field in fields])  # value and do_style
        # Get field condition & aggre function
        field_cond_dict = {}
        aggre_func_dict = {}
        field_style_dict = {}
        style_cond_dict = {}
        pair_fields = []  # I.e., ('debit${value and . or .}@{sum}', 'debit')
        for field in fields:
            temp_field, eval_cond = co.get_field_condition(field)
            eval_cond = eval_cond or 'value or ""'
            temp_field, field_style = co.get_field_style(temp_field)
            temp_field, style_cond = co.get_field_style_cond(temp_field)
            raw_field, aggre_func = co.get_field_aggregation(temp_field)
            # Dict of all special conditions
            field_cond_dict.update({field: eval_cond})
            aggre_func_dict.update({field: aggre_func})
            field_style_dict.update({field: field_style})
            style_cond_dict.update({field: style_cond})
            # --
            pair_fields.append((field, raw_field))
        for line in lines:
            for field in pair_fields:  # (field, raw_field)
                value = self._get_field_data(field[1], line)
                eval_cond = field_cond_dict[field[0]]
                eval_context = \
                    self.get_eval_context(line._name, line, value)
                if eval_cond:
                    value = safe_eval(eval_cond, eval_context)
                # style w/Cond takes priority
                style_cond = style_cond_dict[field[0]]
                style = self._eval_style_cond(line._name, line,
                                              value, style_cond)
                if style is None:
                    style = False  # No style
                elif style is False:
                    style = field_style_dict[field[0]]  # Use default style
                vals[field[0]].append((value, style))
        return (vals, aggre_func_dict,)

    @api.model
    def _eval_style_cond(self, model, record, value, style_cond):
        eval_context = self.get_eval_context(model, record, value)
        field = style_cond = style_cond or '#??'
        styles = {}
        for i in range(style_cond.count('#{')):
            i += 1
            field, style = co.get_field_style(field)
            styles.update({i: style})
            style_cond = style_cond.replace('#{%s}' % style, str(i))
        if not styles:
            return False
        res = safe_eval(style_cond, eval_context)
        if res is None or res is False:
            return res
        return styles[res]

    @api.model
    def _fill_workbook_data(self, workbook, record, data_dict):
        """ Fill data from record with style in data_dict to workbook """
        if not record or not data_dict:
            return
        try:
            for sheet_name in data_dict:
                ws = data_dict[sheet_name]
                st = False
                if isinstance(sheet_name, str):
                    st = co.openpyxl_get_sheet_by_name(workbook, sheet_name)
                elif isinstance(sheet_name, int):
                    if sheet_name > len(workbook.worksheets):
                        raise Exception(_('Not enough worksheets'))
                    st = workbook.worksheets[sheet_name - 1]
                if not st:
                    raise ValidationError(
                        _('Sheet %s not found') % sheet_name)
                # Fill data, header and rows
                self._fill_head(ws, st, record)
                self._fill_lines(ws, st, record)
        except KeyError as e:
            raise ValidationError(_('Key Error\n%s') % e)
        except IllegalCharacterError as e:
            raise ValidationError(
                _('IllegalCharacterError\n'
                  'Some exporting data contain special character\n%s') % e)
        except Exception as e:
            raise ValidationError(
                _('Error filling data into Excel sheets\n%s') % e)

    @api.model
    def _get_field_data(self, _field, _line):
        """ Get field data, and convert data type if needed """
        if not _field:
            return None
        line_copy = _line
        for f in _field.split('.'):
            line_copy = line_copy[f]
        if isinstance(line_copy, str):
            line_copy = line_copy.encode('utf-8')
        return line_copy

    @api.model
    def _fill_head(self, ws, st, record):
        for rc, field in ws.get('_HEAD_', {}).items():
            tmp_field, eval_cond = co.get_field_condition(field)
            eval_cond = eval_cond or 'value or ""'
            tmp_field, field_style = co.get_field_style(tmp_field)
            tmp_field, style_cond = co.get_field_style_cond(tmp_field)
            value = tmp_field and self._get_field_data(tmp_field, record)
            # Eval
            eval_context = self.get_eval_context(record._name,
                                                 record, value)
            if eval_cond:
                value = safe_eval(eval_cond, eval_context)
            if value is not None:
                st[rc] = value
            fc = not style_cond and True or \
                safe_eval(style_cond, eval_context)
            if field_style and fc:  # has style and pass style_cond
                styles = self.env['xlsx.styles'].get_openpyxl_styles()
                co.fill_cell_style(st[rc], field_style, styles)

    @api.model
    def _fill_lines(self, ws, st, record):
        line_fields = list(ws)
        if '_HEAD_' in line_fields:
            line_fields.remove('_HEAD_')
        cont_row = 0  # last data row to continue
        for line_field in line_fields:
            fields = ws.get(line_field, {}).values()
            vals, func = self._get_line_vals(record, line_field, fields)
            is_cont = '_CONT_' in line_field and True or False  # continue row
            cont_set = 0
            rows_inserted = False  # flag to insert row
            for rc, field in ws.get(line_field, {}).items():
                col, row = co.split_row_col(rc)  # starting point
                # Case continue, start from the last data row
                if is_cont and not cont_set:  # only once per line_field
                    cont_set = cont_row + 1
                if is_cont:
                    row = cont_set
                    rc = '%s%s' % (col, cont_set)
                i = 0
                new_row = 0
                new_rc = False
                row_count = len(vals[field])
                # Insert rows to preserve total line
                if not rows_inserted:
                    rows_inserted = True
                    st.insert_rows(row+1, amount=row_count-1)
                # --
                for (row_val, style) in vals[field]:
                    new_row = row + i
                    new_rc = '%s%s' % (col, new_row)
                    row_val = co.adjust_cell_formula(row_val, i)
                    if row_val not in ('None', None):
                        st[new_rc] = co.str_to_number(row_val)
                    if style:
                        styles = self.env['xlsx.styles'].get_openpyxl_styles()
                        co.fill_cell_style(st[new_rc], style, styles)
                    i += 1
                # Add footer line if at least one field have sum
                f = func.get(field, False)
                if f and new_row > 0:
                    new_row += 1
                    f_rc = '%s%s' % (col, new_row)
                    st[f_rc] = '=%s(%s:%s)' % (f, rc, new_rc)
                    co.fill_cell_style(st[f_rc], style, styles)
                cont_row = cont_row < new_row and new_row or cont_row
        return

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
        ConfParam = self.env['ir.config_parameter'].sudo()
        ptemp = ConfParam.get_param('path_temp_file') or '/tmp'
        stamp = dt.utcnow().strftime('%H%M%S%f')[:-3]
        ftemp = '%s/temp%s.xlsx' % (ptemp, stamp)
        f = open(ftemp, 'wb')
        f.write(decoded_data)
        f.seek(0)
        f.close()
        # Workbook created, temp file removed
        wb = load_workbook(ftemp)
        os.remove(ftemp)
        # Start working with workbook
        record = res_model and self.env[res_model].browse(res_id) or False
        self._fill_workbook_data(wb, record, export_dict)
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
        # CSV (convert only on 1st sheet)
        if template.to_csv:
            delimiter = template.csv_delimiter
            out_file = co.csv_from_excel(out_file, delimiter,
                                         template.csv_quote)
            out_ext = template.csv_extension
        return (out_file, '%s.%s' % (out_name, out_ext))
