# Copyright (C) 2015 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from lxml import etree

from odoo import models, fields, api, osv
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SqlFileWizard(models.TransientModel):
    _name = "sql.file.wizard"
    _description = "Allow the user to save the file with sql request's data"

    binary_file = fields.Binary('File', readonly=True)
    file_name = fields.Char('File Name', readonly=True)
    sql_export_id = fields.Many2one(comodel_name='sql.export', required=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """
        Display dynamically parameter fields depending on the sql_export.
        """
        res = super(SqlFileWizard, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        export_obj = self.env['sql.export']
        if view_type == 'form':
            sql_export = export_obj.browse(self.env.context.get('active_id'))
            if sql_export.field_ids:
                eview = etree.fromstring(res['arch'])
                group = etree.Element(
                    'group', name="variables_group", colspan="4")
                toupdate_fields = []
                for field in sql_export.field_ids:
                    toupdate_fields.append(field.name)
                    view_field = etree.SubElement(
                        group, 'field', name=field.name)
                    osv.orm.setup_modifiers(
                        view_field, self.fields_get(field.name))

                res['fields'].update(self.fields_get(toupdate_fields))
                placeholder = eview.xpath(
                    "//separator[@string='variables_placeholder']")[0]
                placeholder.getparent().replace(
                    placeholder, group)
                res['arch'] = etree.tostring(eview, pretty_print=True)
        return res

    def export_sql(self):
        self.ensure_one()
        sql_export = self.sql_export_id

        # Manage Params
        variable_dict = {}
        now_tz = fields.Datetime.context_timestamp(sql_export, datetime.now())
        date = now_tz.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if sql_export.field_ids:
            for field in sql_export.field_ids:
                variable_dict[field.name] = self[field.name]
        if "%(company_id)s" in sql_export.query:
            variable_dict['company_id'] = self.env.user.company_id.id
        if "%(user_id)s" in sql_export.query:
            variable_dict['user_id'] = self.env.uid

        # Execute Request
        res = sql_export._execute_sql_request(
            params=variable_dict, mode='stdout',
            copy_options=sql_export.copy_options)
        if self.sql_export_id.encoding:
            res = res.decode(self.sql_export_id.encoding)
        self.write({
            'binary_file': res,
            'file_name': '%(name)s_%(date)s.csv' % {
                'name': sql_export.name, 'date': date}
        })
        return {
            'view_mode': 'form',
            'res_model': 'sql.file.wizard',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context,
            'nodestroy': True,
        }
