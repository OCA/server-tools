# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Akretion (<http://www.akretion.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import StringIO
import base64
import datetime
import re
from openerp import models, fields, api, _, exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SqlExport(models.Model):
    _name = "sql.export"
    _description = "SQL export"

    PROHIBITED_WORDS = [
        'delete',
        'drop',
        'insert',
        'alter',
        'truncate',
        'execute',
        'create',
        'update'
    ]

    @api.multi
    def _check_query_allowed(self):
        for obj in self:
            query = obj.query.lower()
            for word in self.PROHIBITED_WORDS:
                expr = r'\b%s\b' % word
                is_not_safe = re.search(expr, query)
                if is_not_safe:
                    return False
        return True

    @api.model
    def _get_editor_group(self):
        ir_model_obj = self.env['ir.model.data']
        return [ir_model_obj.xmlid_to_res_id(
            'sql_export.group_sql_request_editor')]

    name = fields.Char('Name', required=True)
    query = fields.Text(
        'Query',
        required=True,
        help="You can't use the following word : delete, drop, create, "
             "insert, alter, truncate, execute, update")
    copy_options = fields.Char(
        'Copy Options',
        required=True,
        default="CSV HEADER DELIMITER ';'")
    group_ids = fields.Many2many(
        'res.groups',
        'groups_sqlquery_rel',
        'sql_id',
        'group_id',
        'Allowed Groups',
        default=_get_editor_group)
    user_ids = fields.Many2many(
        'res.users',
        'users_sqlquery_rel',
        'sql_id',
        'user_id',
        'Allowed Users')

    _constraints = [(_check_query_allowed,
                     'The query you want make is not allowed : prohibited '
                     'actions (%s)' % ', '.join(PROHIBITED_WORDS),
                     ['query'])]

    @api.multi
    def export_sql_query(self):
        for obj in self:
            today = datetime.datetime.now()
            today_tz = fields.Datetime.context_timestamp(
                obj, today)
            date = today_tz.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            output = StringIO.StringIO()
            query = "COPY (" + obj.query + ")  TO STDOUT WITH " + \
                    obj.copy_options
            self.env.cr.copy_expert(query, output)
            output.getvalue()
            new_output = base64.b64encode(output.getvalue())
            output.close()
            wiz = self.env['sql.file.wizard'].create(
                {
                    'binary_file': new_output,
                    'file_name': obj.name + '_' + date + '.csv'})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sql.file.wizard',
            'res_id': wiz.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
            'nodestroy': True,
        }

    @api.model
    def check_query_syntax(self, vals):
        if vals.get('query', False):
            vals['query'] = vals['query'].strip()
            if vals['query'][-1] == ';':
                vals['query'] = vals['query'][:-1]
            try:
                self.env.cr.execute(vals['query'])
            except:
                self.env.cr.rollback()
                raise exceptions.Warning(
                    _("The Sql query is not valid."))
        return vals

    @api.multi
    def write(self, vals):
        vals = self.check_query_syntax(vals)
        return super(SqlExport, self).write(vals)

    @api.model
    def create(self, vals):
        vals = self.check_query_syntax(vals)
        return super(SqlExport, self).create(vals)
