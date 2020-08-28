# Copyright (C) 2015 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class SqlExport(models.Model):
    _name = "sql.export"
    _inherit = ['sql.request.mixin']
    _description = "SQL export"

    _sql_request_groups_relation = 'groups_sqlquery_rel'

    _sql_request_users_relation = 'users_sqlquery_rel'

    _check_execution_enabled = False

    copy_options = fields.Char(
        string='Copy Options', required=False,
        default="CSV HEADER DELIMITER ';'")

    file_format = fields.Selection(
        [('csv', 'CSV')],
        default='csv',
        required=True)

    field_ids = fields.Many2many(
        'ir.model.fields',
        'fields_sqlquery_rel',
        'sql_id',
        'field_id',
        'Parameters',
        domain=[('model', '=', 'sql.file.wizard')])

    encoding = fields.Selection(
        [('utf-8', 'utf-8'), ('utf-16', 'utf-16'),
         ('windows-1252', 'windows-1252'), ('latin1', 'latin1'),
         ('latin2', 'latin2'), ('big5', 'big5'), ('gb18030', 'gb18030'),
         ('shift_jis', 'shift_jis'), ('windows-1251', 'windows-1251'),
         ('koir8_r', 'koir8_r')], string='Encoding', required=True,
        default='utf-8')

    def export_sql_query(self):
        self.ensure_one()
        wiz = self.env['sql.file.wizard'].create({
            'sql_export_id': self.id})
        return {
            'view_mode': 'form',
            'res_model': 'sql.file.wizard',
            'res_id': wiz.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context,
            'nodestroy': True,
        }

    def _get_file_extension(self):
        self.ensure_one()
        if self.file_format == 'csv':
            return 'csv'

    def csv_get_data_from_query(self, variable_dict):
        self.ensure_one()
        # Execute Request
        res = self._execute_sql_request(
            params=variable_dict, mode='stdout',
            copy_options=self.copy_options)
        if self.encoding:
            res = res.decode(self.encoding)
        return res
