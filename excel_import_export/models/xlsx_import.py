# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import base64
import uuid
import xlrd
import xlwt
import time
import unicodecsv
import codecs
import csv
from io import BytesIO
from . import common as co
from ast import literal_eval
from datetime import date, datetime as dt
from odoo.tools.float_utils import float_compare
from odoo import models, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval as eval


class XLSXImport(models.AbstractModel):
    _name = 'xlsx.import'

    @api.model
    def get_eval_context(self, model=False, value=False):
        eval_context = {'float_compare': float_compare,
                        'time': time,
                        'datetime': dt,
                        'date': date,
                        'env': self.env,
                        'context': self._context,
                        'value': False,
                        'model': False,
                        }
        if model:
            eval_context.update({'model': self.env[model]})
        if value:
            if isinstance(value, str):  # Remove non Ord 128 character
                value = ''.join([i if ord(i) < 128 else ' ' for i in value])
            eval_context.update({'value': value})
        return eval_context

    @api.model
    def get_external_id(self, record):
        """ Get external ID of the record, if not exists create one """
        ModelData = self.env['ir.model.data']
        xml_id = record.get_external_id()
        if not xml_id or (record.id in xml_id and xml_id[record.id] == ''):
            ModelData.create({'name': '%s_%s' % (record._table, record.id),
                              'module': 'excel_import_export',
                              'model': record._name,
                              'res_id': record.id, })
            xml_id = record.get_external_id()
        return xml_id[record.id]

    @api.model
    def _get_field_type(self, model, field):
        """ Get 2 field type """
        try:
            record = self.env[model].new()
            for f in field.split('/'):
                field_type = record._fields[f].type
                if field_type in ('one2many', 'many2many'):
                    record = record[f]
                else:
                    return field_type
        except Exception:
            raise ValidationError(
                _('Invalid declaration, %s has no valid field type') % field)

    @api.model
    def _get_field_types(self, model, fields):
        """ Get multiple field type """
        field_types = {}
        for field in fields:
            field_type = self._get_field_type(model, field)
            field_types[field] = field_type
        return field_types

    @api.model
    def _delete_record_data(self, record, data_dict):
        """ Fill data from record with format in data_dict to workbook """
        if not record or not data_dict:
            return
        try:
            for sheet_name in data_dict:
                worksheet = data_dict[sheet_name]
                # Get delete condition, if not specified, delete all
                line_del_dom = worksheet.get('_LINE_DELETE_DOMAIN_', {})
                line_fields = filter(lambda x: x not in
                                     ('_HEAD_', '_LINE_DELETE_DOMAIN_'),
                                     worksheet)
                for line_field in line_fields:
                    line_field, _ = co.get_line_max(line_field)
                    if line_field in record and record[line_field]:
                        model = self.env[record[line_field]._name]
                        lines = model.search(
                            [('id', 'in', record[line_field].ids)] +
                            line_del_dom.get(line_field, []))
                        lines.unlink()
        except Exception as e:
            raise ValidationError(_('Error deleting data\n%s') % e)

    @api.model
    def _get_line_vals(self, st, worksheet, model, line_field):
        """ Get values of this field from excel sheet """
        new_line_field, max_row = co.get_line_max(line_field)
        vals = {}
        for rc, columns in worksheet.get(line_field, {}).items():
            if not isinstance(columns, list):  # Ex. 'A1': ['field1', 'field2']
                columns = [columns]
            for field in columns:
                rc, key_eval_cond = co.get_field_condition(rc)
                x_field, val_eval_cond = co.get_field_condition(field)
                row, col = co.pos2idx(rc)
                out_field = '%s/%s' % (new_line_field, x_field)
                field_type = self._get_field_type(model, out_field)
                vals.update({out_field: []})
                # Case default value from an eval
                for idx in range(row, st.nrows):
                    if max_row and (idx - row) > (max_row - 1):
                        break
                    value = co._get_cell_value(st.cell(idx, col),
                                               field_type=field_type)
                    eval_context = self.get_eval_context(model=model,
                                                         value=value)
                    if key_eval_cond:
                        # str() will throw cordinal not in range error
                        # value = str(eval(key_eval_cond, eval_context))
                        value = eval(key_eval_cond, eval_context)
                    # Case Eval
                    if val_eval_cond:
                        # value = str(eval(val_eval_cond, eval_context))
                        value = eval(val_eval_cond, eval_context)
                    vals[out_field].append(value)
                # if all value in vals[out_field] == '', we don't need it
                if not filter(lambda x: x != '', vals[out_field]):
                    vals.pop(out_field)
        return vals

    @api.model
    def _import_record_data(self, import_file, record, data_dict):
        """ From complex excel template, create temp simple excel,
        and prepare to convert to CSV to load """
        if not data_dict:
            return
        try:
            decoded_data = base64.decodestring(import_file)
            wb = xlrd.open_workbook(file_contents=decoded_data)
            # Create output xls, begins with id column
            col_idx = 0  # Starting column
            out_wb = xlwt.Workbook()
            out_st = out_wb.add_sheet("Sheet 1")
            xml_id = record and self.get_external_id(record) or \
                '%s.%s' % ('xls', uuid.uuid4())
            out_st.write(0, 0, 'id')
            out_st.write(1, 0, xml_id)
            col_idx += 1
            model = record._name
            for sheet_name in data_dict:  # For each Sheet
                worksheet = data_dict[sheet_name]
                st = False
                if isinstance(sheet_name, str):
                    st = co.xlrd_get_sheet_by_name(wb, sheet_name)
                elif isinstance(sheet_name, int):
                    st = wb.sheet_by_index(sheet_name - 1)
                if not st:
                    raise ValidationError(
                        _('Sheet %s not found') % sheet_name)
                # HEAD(s)
                for rc, field in worksheet.get('_HEAD_', {}).items():
                    rc, key_eval_cond = co.get_field_condition(rc)
                    field, val_eval_cond = co.get_field_condition(field)
                    field_type = self._get_field_type(model, field)
                    value = False
                    try:
                        row, col = co.pos2idx(rc)
                        value = co._get_cell_value(st.cell(row, col),
                                                   field_type=field_type)
                    except Exception:
                        pass
                    eval_context = self.get_eval_context(model=model,
                                                         value=value)
                    if key_eval_cond:
                        value = str(eval(key_eval_cond, eval_context))
                    # Case Eval
                    if val_eval_cond:
                        value = str(eval(val_eval_cond, eval_context))
                    # --
                    out_st.write(0, col_idx, field)  # Next Column
                    out_st.write(1, col_idx, value)  # Next Value
                    col_idx += 1
                # Line Items
                line_fields = filter(lambda x: x not in
                                     ('_HEAD_', '_LINE_DELETE_DOMAIN_'),
                                     worksheet)
                for line_field in line_fields:
                    vals = self._get_line_vals(st, worksheet,
                                               model, line_field)
                    for field in vals:
                        # Columns, i.e., line_ids/field_id
                        out_st.write(0, col_idx, field)
                        # Data
                        i = 1
                        for value in vals[field]:
                            out_st.write(i, col_idx, value)
                            i += 1
                        col_idx += 1
            content = BytesIO()
            out_wb.save(content)
            content.seek(0)  # Set index to 0, and start reading
            xls_file = base64.encodestring(content.read())
            self.import_excel(model, xls_file, header_map=False,
                              extra_columns=False, auto_id=True, force_id=True)
            return self.env.ref(xml_id)
        except xlrd.XLRDError:
            raise ValidationError(
                _('Invalid file format, only .xls or .xlsx file allowed'))
        except Exception as e:
            raise ValidationError(_('Error importing data\n%s') % e)

    @api.model
    def import_excel(self, model, file, header_map=None,
                     extra_columns=None, auto_id=False,
                     force_id=False):
        # 1) Convert form XLS to CSV
        header_fields, file_txt = self.xls_to_csv(
            model, file, header_map=header_map,
            extra_columns=extra_columns, auto_id=auto_id,
            force_id=force_id)
        # 2) Do the import
        xls_ids = self.import_csv(model, header_fields, file_txt)
        return xls_ids

    @api.model
    def xls_to_csv(self, model, file,
                   header_map=None, extra_columns=None,
                   auto_id=False, force_id=False):
        """ This function will convert a simple (header+line) XLS file to
            simple CSV file (header+line) and the header columns
        To map user column with database column
        - header_map = {'Name': 'name', 'Document', 'doc_id', }
        If there is additional fixed column value
        - extra_columns = [('name', 'ABC'), ('id', 10), ]
        If the import file have column id, we will use this column to create
            external id, and hence possible to return record id being created
        if auto_id=True, system will add id field with running number
        if force_id=True, system will use ID from the original excel
            force_id=False, system will replace ID with UUID
        Return:
            - csv ready for import to Odoo
              'ID', 'Asset', ...
              'external_id_1', 'ASSET-0001', ...
              'external_id_2', 'ASSET-0002', ...
            - headers, i.e,
              ['id', 'asset_id', ...]
        """
        try:
            decoded_data = base64.decodestring(file)
            wb = xlrd.open_workbook(file_contents=decoded_data)
        except xlrd.XLRDError:
            raise ValidationError(
                _('Invalid file format, only .xls or .xlsx file allowed'))
        except Exception:
            raise
        st = wb.sheet_by_index(0)
        csv_file = BytesIO()
        csv_out = unicodecsv.writer(csv_file,
                                    encoding='utf-8',
                                    quoting=unicodecsv.QUOTE_ALL)
        _HEADER_FIELDS = []
        if st._cell_values:
            _HEADER_FIELDS = st._cell_values[0]
        # Map column name
        if header_map:
            _HEADER_FIELDS = [header_map.get(x.lower().strip(), False) and
                              header_map[x.lower()] or False
                              for x in _HEADER_FIELDS]
        id_index = -1  # -1 means no id
        for nrow in xrange(st.nrows):
            if nrow == 0:  # Header, find id field
                header_values = [x.lower().strip()
                                 for x in st.row_values(nrow)]
                if 'id' in header_values:
                    id_index = header_values.index('id')
            if nrow > 0:
                row_values = st.row_values(nrow)
                field_types = self._get_field_types(model, _HEADER_FIELDS)
                for index, val in enumerate(row_values):
                    # Get Odoo field type
                    field = _HEADER_FIELDS[index]
                    # If id field, do not specify field_type
                    field_type = field != 'id' and field_types[field] or False
                    if id_index == index and val and not force_id:
                        # UUID replace id
                        xml_id = '%s.%s' % ('xls', uuid.uuid4())
                        row_values[index] = xml_id
                    else:
                        cell = st.cell(nrow, index)
                        row_values[index] = \
                            co._get_cell_value(cell, field_type=field_type)
                csv_out.writerow(row_values)
            else:
                csv_out.writerow(st.row_values(nrow))
        csv_file.seek(0)
        file_txt = csv_file.read()
        csv_file.close()
        if not file_txt:
            raise ValidationError(_(str("File Not found.")))
        # Create xml_ids if not already assigned
        if id_index == -1:
            _HEADER_FIELDS.insert(0, 'id')
            if auto_id:
                file_txt = co._add_id_column(file_txt)
            else:
                xml_id = '%s.%s' % ('xls', uuid.uuid4())
                file_txt = co._add_column('id', xml_id, file_txt)
        # Add extra column
        if extra_columns:
            for column in extra_columns:
                _HEADER_FIELDS.insert(0, str(column[0]))
                file_txt = co._add_column(column[0], column[1], file_txt)
        return (_HEADER_FIELDS, file_txt)

    @api.model
    def import_csv(self, model, header_fields, csv_txt, csv_header=True):
        """
        The csv_txt loaded, must also have the header row
        - header_fields i.e, ['id', 'field1', 'field2']
        - csv_txt = normal csv with comma delimited
        - csv_header = True (default), if csv_txt contain header row
        """
        # get xml_ids
        f = BytesIO(csv_txt)
        rows = csv.reader(codecs.iterdecode(f, 'utf-8'), delimiter=',')
        id_index = -1
        xml_ids = []
        head_row = [isinstance(x, str) and x.lower() or ''
                    for x in header_fields]
        id_index = head_row.index('id')
        if id_index >= 0:
            for idx, row in enumerate(rows):
                if csv_header and idx == 0:
                    continue
                if isinstance(row[id_index], str) and \
                        len(row[id_index].strip()) > 0:
                    xml_ids.append(row[id_index])
        # Do the import
        Import = self.env['base_import.import']
        imp = Import.create({
            'res_model': model,
            'file': csv_txt,
            'file_name': 'temp.csv',
        })
        errors = imp.do(
            header_fields,
            {'headers': csv_header,
             'separator': ',',
             'quoting': '"',
             'encoding': 'utf-8',
             })
        if errors:
            if errors[0]['message'] == ("Unknown error during import: "
                                        "<type 'exceptions.TypeError'>: "
                                        "'bool' object is not iterable"):
                raise ValidationError(
                    _('Data not valid or no data to import'))
            else:
                raise ValidationError(errors[0]['message'].encode('utf-8'))
        return xml_ids

    @api.model
    def _post_import_operation(self, record, operations):
        """ Run python code after import """
        if not record or not operations:
            return
        try:
            if not isinstance(operations, list):
                operations = [operations]
            for operation in operations:
                if '${' in operation:
                    code = (operation.split('${'))[1].split('}')[0]
                    eval_context = {'object': record}
                    eval(code, eval_context)
        except Exception as e:
            raise ValidationError(_('Post import operation error\n%s') % e)

    @api.model
    def import_xlsx(self, import_file, template, res_model, res_id=False):
        """
        - If res_id = False, we want to create new document first
        - Delete fields' data according to data_dict['__IMPORT__']
        - Import data from excel according to data_dict['__IMPORT__']
        """
        self = self.sudo()
        if template.res_model != res_model:
            raise ValidationError(_("Template's model mismatch"))
        record = self.env[res_model].browse(res_id)
        data_dict = literal_eval(template.instruction.strip())
        if not data_dict.get('__IMPORT__'):
            raise ValidationError(
                _("No data_dict['__IMPORT__'] in template %s") % template.name)
        if record:
            # Delete existing data first
            self._delete_record_data(record, data_dict['__IMPORT__'])
        # Fill up record with data from excel sheets
        record = self._import_record_data(import_file, record,
                                          data_dict['__IMPORT__'])
        # Post Import Operation, i.e., cleanup some data
        if data_dict.get('__POST_IMPORT__', False):
            self._post_import_operation(record, data_dict['__POST_IMPORT__'])
        return record
