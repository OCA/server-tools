# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import datetime

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class Export(models.Model):
    _name = "export"
    _description = 'Data Export Record'

    name = fields.Char()
    model_id = fields.Many2one(
        'ir.model',
        string='Exported Model',
        readonly=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Exported by',
        readonly=True,
    )
    field_ids = fields.Many2many(
        'ir.model.fields',
        string='Exported Fields',
        readonly=True,
    )
    record_ids = fields.Many2many(
        'ir.model.data',
        string='Exported Records',
        readonly=True,
    )

    @api.model
    def log_export(self, recordset, field_names):
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S (UTC)')
        model_name = recordset._name
        model = self.env['ir.model'].search([('model', '=', model_name)])
        user = self.env.user
        name = '{} / {} / {}'.format(date, model.name, user.name)
        field_ids = self.env['ir.model.fields'].search([
            ('model', '=', model_name),
            ('name', 'in', field_names),
        ]).ids
        record_ids = self.env['ir.model.data'].search([
            ('model', '=', model_name),
            ('res_id', 'in', recordset.ids),
        ]).ids
        export = self.create({
            'name': name,
            'model_id': model.id,
            'field_ids': [(4, field_ids)],
            'record_ids': [(4, record_ids)],
            'user_id': user.id,
        })
        export.sudo().post_notification()
        return export

    @api.multi
    def post_notification(self):
        channel_id = self.env.ref('base_export_security.export_channel').id
        channel = self.env['mail.channel'].search([('id', '=', channel_id)])
        records = len(self.record_ids.ids)
        model = self.model_id.name
        user = self.user_id.name
        field_labels = ', '.join(
            self.field_ids.sorted().mapped('field_description'),
        )
        message_body = _(
            ('{} <b>{}</b> records exported by <b>{}</b>.<br /><b>Fields '
             'exported:</b> {}').format(records, model, user, field_labels),
        )
        message = channel.message_post(
            body=message_body,
            message_type='notification',
            subtype='mail.mt_comment',
        )
        return message


export_data_original = models.BaseModel.export_data


@api.multi
def export_data(self, fields_to_export, raw_data=False):
    if self.env.user.has_group('base_export_security.export_group'):
        field_names = map(
            lambda path_array: path_array[0], map(
                models.fix_import_export_id_paths,
                fields_to_export,
            ),
        )
        self.env['export'].log_export(self, field_names)
        return export_data_original(self, fields_to_export, raw_data)
    else:
        raise AccessError(
            _('You do not have permission to export data'),
        )


models.BaseModel.export_data = export_data
