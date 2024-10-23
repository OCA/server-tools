# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import os
import base64
from ast import literal_eval
from odoo import api, fields, models, _
from odoo.modules.module import get_module_path
from os.path import join as opj
from . import common as co
from odoo.exceptions import ValidationError


class XLSXTemplate(models.Model):
    """ Master Data for XLSX Templates
    - Excel Template
    - Import/Export Meta Data (dict text)
    - Default values, etc.
    """
    _name = 'xlsx.template'
    _description = 'Excel template file and instruction'
    _order = 'name'

    name = fields.Char(
        string='Template Name',
        required=True,
    )
    res_model = fields.Char(
        string='Resource Model',
        help="The database object this attachment will be attached to.",
    )
    fname = fields.Char(
        string='File Name',
    )
    gname = fields.Char(
        string='Group Name',
        help="Multiple template of same model, can belong to same group,\n"
        "result in multiple template selection",
    )
    description = fields.Char(
        string='Description',
    )
    input_instruction = fields.Text(
        string='Instruction (Input)',
        help="This is used to construct instruction in tab Import/Export",
    )
    instruction = fields.Text(
        string='Instruction',
        compute='_compute_output_instruction',
        help="Instruction on how to import/export, prepared by system."
    )
    datas = fields.Binary(
        string='File Content',
    )
    to_csv = fields.Boolean(
        string='Convert to CSV?',
        default=False,
    )
    csv_delimiter = fields.Char(
        string='CSV Delimiter',
        size=1,
        default=',',
        required=True,
        help="Optional for CSV, default is comma.",
    )
    csv_extension = fields.Char(
        string='CSV File Extension',
        size=5,
        default='csv',
        required=True,
        help="Optional for CSV, default is .csv"
    )
    csv_quote = fields.Boolean(
        string='CSV Quoting',
        default=True,
        help="Optional for CSV, default is full quoting."
    )
    export_ids = fields.One2many(
        comodel_name='xlsx.template.export',
        inverse_name='template_id',
    )
    import_ids = fields.One2many(
        comodel_name='xlsx.template.import',
        inverse_name='template_id',
    )
    post_import_hook = fields.Char(
        string='Post Import Function Hook',
        help="Call a function after successful import, i.e.,\n"
        "${object.post_import_do_something()}",
    )
    show_instruction = fields.Boolean(
        string='Show Output',
        default=False,
        help="This is the computed instruction based on tab Import/Export,\n"
        "to be used by xlsx import/export engine",
    )
    redirect_action = fields.Many2one(
        comodel_name='ir.actions.act_window',
        string='Return Action',
        domain=[('type', '=', 'ir.actions.act_window')],
        help="Optional action, redirection after finish import operation",
    )

    @api.multi
    @api.constrains('redirect_action', 'res_model')
    def _check_action_model(self):
        for rec in self:
            if rec.res_model and rec.redirect_action and \
                    rec.res_model != rec.redirect_action.res_model:
                raise ValidationError(_('The selected redirect action is '
                                        'not for model %s') % rec.res_model)

    @api.model
    def load_xlsx_template(self, tempalte_ids, addon=False):
        for template in self.browse(tempalte_ids):
            if not addon:
                addon = list(template.get_external_id().
                             values())[0].split('.')[0]
            addon_path = get_module_path(addon)
            file_path = False
            for root, dirs, files in os.walk(addon_path):
                for name in files:
                    if name == template.fname:
                        file_path = os.path.abspath(opj(root, name))
            if file_path:
                template.datas = base64.b64encode(open(file_path, 'rb').read())
        return True

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if vals.get('input_instruction'):
            rec._compute_input_export_instruction()
            rec._compute_input_import_instruction()
            rec._compute_input_post_import_hook()
        return rec

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if vals.get('input_instruction'):
            for rec in self:
                rec._compute_input_export_instruction()
                rec._compute_input_import_instruction()
                rec._compute_input_post_import_hook()
        return res

    @api.multi
    def _compute_input_export_instruction(self):
        self = self.with_context(compute_from_input=True)
        for rec in self:
            # Export Instruction
            input_dict = literal_eval(rec.input_instruction.strip())
            rec.export_ids.unlink()
            export_dict = input_dict.get('__EXPORT__')
            if not export_dict:
                continue
            export_lines = []
            sequence = 0
            # Sheet
            for sheet, rows in export_dict.items():
                sequence += 1
                vals = {'sequence': sequence,
                        'section_type': 'sheet',
                        'sheet': str(sheet),
                        }
                export_lines.append((0, 0, vals))
                # Rows
                for row_field, lines in rows.items():
                    sequence += 1
                    is_cont = False
                    if '_CONT_' in row_field:
                        is_cont = True
                        row_field = row_field.replace('_CONT_', '')
                    is_extend = False
                    if "_EXTEND_" in row_field:
                        is_extend = True
                        row_field = row_field.replace("_EXTEND_", "")
                    vals = {'sequence': sequence,
                            'section_type': (row_field == '_HEAD_' and
                                             'head' or 'row'),
                            'row_field': row_field,
                            'is_cont': is_cont,
                            'is_extend': is_extend,
                            }
                    export_lines.append((0, 0, vals))
                    for excel_cell, field_name in lines.items():
                        sequence += 1
                        vals = {'sequence': sequence,
                                'section_type': 'data',
                                'excel_cell': excel_cell,
                                'field_name': field_name,
                                }
                        export_lines.append((0, 0, vals))
            rec.write({'export_ids': export_lines})

    @api.multi
    def _compute_input_import_instruction(self):
        self = self.with_context(compute_from_input=True)
        for rec in self:
            # Import Instruction
            input_dict = literal_eval(rec.input_instruction.strip())
            rec.import_ids.unlink()
            import_dict = input_dict.get('__IMPORT__')
            if not import_dict:
                continue
            import_lines = []
            sequence = 0
            # Sheet
            for sheet, rows in import_dict.items():
                sequence += 1
                vals = {'sequence': sequence,
                        'section_type': 'sheet',
                        'sheet': str(sheet),
                        }
                import_lines.append((0, 0, vals))
                # Rows
                for row_field, lines in rows.items():
                    sequence += 1
                    no_delete = False
                    if '_NODEL_' in row_field:
                        no_delete = True
                        row_field = row_field.replace('_NODEL_', '')
                    vals = {'sequence': sequence,
                            'section_type': (row_field == '_HEAD_' and
                                             'head' or 'row'),
                            'row_field': row_field,
                            'no_delete': no_delete,
                            }
                    import_lines.append((0, 0, vals))
                    for excel_cell, field_name in lines.items():
                        sequence += 1
                        vals = {'sequence': sequence,
                                'section_type': 'data',
                                'excel_cell': excel_cell,
                                'field_name': field_name,
                                }
                        import_lines.append((0, 0, vals))
            rec.write({'import_ids': import_lines})

    @api.multi
    def _compute_input_post_import_hook(self):
        self = self.with_context(compute_from_input=True)
        for rec in self:
            # Import Instruction
            input_dict = literal_eval(rec.input_instruction.strip())
            rec.post_import_hook = input_dict.get('__POST_IMPORT__')

    @api.multi
    def _compute_output_instruction(self):
        """ From database, compute back to dictionary """
        for rec in self:
            inst_dict = {}
            prev_sheet = False
            prev_row = False
            # Export Instruction
            itype = '__EXPORT__'
            inst_dict[itype] = {}
            for line in rec.export_ids:
                if line.section_type == 'sheet':
                    sheet = co.isinteger(line.sheet) and \
                        int(line.sheet) or line.sheet
                    sheet_dict = {sheet: {}}
                    inst_dict[itype].update(sheet_dict)
                    prev_sheet = sheet
                    continue
                if line.section_type in ('head', 'row'):
                    row_field = line.row_field
                    if line.section_type == 'row' and line.is_cont:
                        row_field = '_CONT_%s' % row_field
                    if line.section_type == "row" and line.is_extend:
                        row_field = "_EXTEND_%s" % row_field
                    row_dict = {row_field: {}}
                    inst_dict[itype][prev_sheet].update(row_dict)
                    prev_row = row_field
                    continue
                if line.section_type == 'data':
                    excel_cell = line.excel_cell
                    field_name = line.field_name or ''
                    field_name += line.field_cond or ''
                    field_name += line.style or ''
                    field_name += line.style_cond or ''
                    if line.is_sum:
                        field_name += '@{sum}'
                    cell_dict = {excel_cell: field_name}
                    inst_dict[itype][prev_sheet][prev_row].update(cell_dict)
                    continue
            # Import Instruction
            itype = '__IMPORT__'
            inst_dict[itype] = {}
            for line in rec.import_ids:
                if line.section_type == 'sheet':
                    sheet = co.isinteger(line.sheet) and \
                        int(line.sheet) or line.sheet
                    sheet_dict = {sheet: {}}
                    inst_dict[itype].update(sheet_dict)
                    prev_sheet = sheet
                    continue
                if line.section_type in ('head', 'row'):
                    row_field = line.row_field
                    if line.section_type == 'row' and line.no_delete:
                        row_field = '_NODEL_%s' % row_field
                    row_dict = {row_field: {}}
                    inst_dict[itype][prev_sheet].update(row_dict)
                    prev_row = row_field
                    continue
                if line.section_type == 'data':
                    excel_cell = line.excel_cell
                    field_name = line.field_name or ''
                    field_name += line.field_cond or ''
                    cell_dict = {excel_cell: field_name}
                    inst_dict[itype][prev_sheet][prev_row].update(cell_dict)
                    continue
            itype = '__POST_IMPORT__'
            inst_dict[itype] = False
            if rec.post_import_hook:
                inst_dict[itype] = rec.post_import_hook
            rec.instruction = inst_dict


class XLSXTemplateImport(models.Model):
    _name = 'xlsx.template.import'
    _description = 'Detailed of how excel data will be imported'
    _order = 'sequence'

    template_id = fields.Many2one(
        comodel_name='xlsx.template',
        string='XLSX Template',
        index=True,
        ondelete='cascade',
        readonly=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    sheet = fields.Char(
        string='Sheet',
    )
    section_type = fields.Selection(
        [('sheet', 'Sheet'),
         ('head', 'Head'),
         ('row', 'Row'),
         ('data', 'Data')],
        string='Section Type',
        required=True,
    )
    row_field = fields.Char(
        string='Row Field',
        help="If section type is row, this field is required",
    )
    no_delete = fields.Boolean(
        string='No Delete',
        default=False,
        help="By default, all rows will be deleted before import.\n"
        "Select No Delete, otherwise"
    )
    excel_cell = fields.Char(
        string='Cell',
    )
    field_name = fields.Char(
        string='Field',
    )
    field_cond = fields.Char(
        string='Field Cond.',
    )

    @api.model
    def create(self, vals):
        new_vals = self._extract_field_name(vals)
        return super().create(new_vals)

    @api.model
    def _extract_field_name(self, vals):
        if self._context.get('compute_from_input') and vals.get('field_name'):
            field_name, field_cond = co.get_field_condition(vals['field_name'])
            field_cond = field_cond and '${%s}' % (field_cond or '') or False
            vals.update({'field_name': field_name,
                         'field_cond': field_cond,
                         })
        return vals


class XLSXTemplateExport(models.Model):
    _name = 'xlsx.template.export'
    _description = 'Detailed of how excel data will be exported'
    _order = 'sequence'

    template_id = fields.Many2one(
        comodel_name='xlsx.template',
        string='XLSX Template',
        index=True,
        ondelete='cascade',
        readonly=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    sheet = fields.Char(
        string='Sheet',
    )
    section_type = fields.Selection(
        [('sheet', 'Sheet'),
         ('head', 'Head'),
         ('row', 'Row'),
         ('data', 'Data')],
        string='Section Type',
        required=True,
    )
    row_field = fields.Char(
        string='Row Field',
        help="If section type is row, this field is required",
    )
    is_cont = fields.Boolean(
        string='Continue',
        default=False,
        help="Continue data rows after last data row",
    )
    is_extend = fields.Boolean(
        string='Extend',
        default=False,
        help="Extend a blank row after filling each record, to extend the footer",
    )
    excel_cell = fields.Char(
        string='Cell',
    )
    field_name = fields.Char(
        string='Field',
    )
    field_cond = fields.Char(
        string='Field Cond.',
    )
    is_sum = fields.Boolean(
        string='Sum',
        default=False,
    )
    style = fields.Char(
        string='Default Style',
    )
    style_cond = fields.Char(
        string='Style w/Cond.',
    )

    @api.model
    def create(self, vals):
        new_vals = self._extract_field_name(vals)
        return super().create(new_vals)

    @api.model
    def _extract_field_name(self, vals):
        if self._context.get('compute_from_input') and vals.get('field_name'):
            field_name, field_cond = co.get_field_condition(vals['field_name'])
            field_cond = field_cond or 'value or ""'
            field_name, style = co.get_field_style(field_name)
            field_name, style_cond = co.get_field_style_cond(field_name)
            field_name, func = co.get_field_aggregation(field_name)
            vals.update({'field_name': field_name,
                         'field_cond': '${%s}' % (field_cond or ''),
                         'style': '#{%s}' % (style or ''),
                         'style_cond': '#?%s?' % (style_cond or ''),
                         'is_sum': func == 'sum' and True or False,
                         })
        return vals
