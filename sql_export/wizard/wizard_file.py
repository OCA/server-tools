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
from openerp import models, fields, api
from openerp.osv.orm import setup_modifiers
import StringIO
import base64
import datetime
from lxml import etree
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import uuid


class SqlFileWizard(models.TransientModel):
    _name = "sql.file.wizard"
    _description = "Allow the user to save the file with sql request's data"

    binary_file = fields.Binary('File', readonly=True)
    file_name = fields.Char('File Name', readonly=True)
    valid = fields.Boolean()
    sql_export_id = fields.Many2one(comodel_name='sql.export', required=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """
        Display dinamicaly parameter fields depending on the sql_export.
        """
        res = super(SqlFileWizard, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        export_obj = self.env['sql.export']
        if view_type == 'form':
            sql_export = export_obj.browse(self._context.get('active_id'))
            if sql_export.field_ids:
                eview = etree.fromstring(res['arch'])
                group = etree.Element(
                    'group', name="variables_group", colspan="4")
                toupdate_fields = []
                for field in sql_export.field_ids:
                    kwargs = {'name': "%s" % field.name}
                    toupdate_fields.append(field.name)
                    view_field = etree.SubElement(group, 'field', **kwargs)
                    setup_modifiers(view_field, self.fields_get(field.name))

                res['fields'].update(self.fields_get(toupdate_fields))
                placeholder = eview.xpath(
                    "//separator[@string='variables_placeholder']")[0]
                placeholder.getparent().replace(
                    placeholder, group)
                res['arch'] = etree.tostring(eview, pretty_print=True)
        return res

    @api.multi
    def export_sql(self):
        self.ensure_one()
        sql_export = self.sql_export_id
        today = datetime.datetime.now()
        today_tz = fields.Datetime.context_timestamp(
            sql_export, today)
        date = today_tz.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        output = StringIO.StringIO()
        variable_dict = {}
        if sql_export.field_ids:
            for field in sql_export.field_ids:
                variable_dict[field.name] = self[field.name]
        if "%(company_id)s" in sql_export.query:
            variable_dict['company_id'] = self.env.user.company_id.id
        if "%(user_id)s" in sql_export.query:
            variable_dict['user_id'] = self._uid
        format_query = self.env.cr.mogrify(sql_export.query, variable_dict)
        query = "COPY (" + format_query + ")  TO STDOUT WITH " + \
                sql_export.copy_options
        name = 'export_query_%s' % uuid.uuid1().hex
        self.env.cr.execute("SAVEPOINT %s" % name)
        try:
            self.env.cr.copy_expert(query, output)
            output.getvalue()
            new_output = base64.b64encode(output.getvalue())
            output.close()
        finally:
            self.env.cr.execute("ROLLBACK TO SAVEPOINT %s" % name)
        wiz = self.write(
            {
                'binary_file': new_output,
                'file_name': sql_export.name + '_' + date + '.csv'})
        if not sql_export.valid:
            sql_export.sudo().valid = True
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sql.file.wizard',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
            'nodestroy': True,
        }
