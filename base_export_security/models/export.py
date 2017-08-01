# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class Export(models.Model):
    _name = 'export.event'
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
        date = fields.Datetime.now()
        model_name = recordset._name
        model = self.env['ir.model'].search([('model', '=', model_name)])
        user = self.env.user
        name_data = {'date': date, 'model': model.name, 'user': user.name}
        name = '%(date)s / %(model)s / %(user)s' % name_data
        exported_fields = self.env['ir.model.fields'].search([
            ('model', '=', model_name),
            ('name', 'in', field_names),
        ])
        records = self.env['ir.model.data'].search([
            ('model', '=', model_name),
            ('res_id', 'in', recordset.ids),
        ])
        export = self.create({
            'name': name,
            'model_id': model.id,
            'field_ids': [(6, 0, exported_fields.ids)],
            'record_ids': [(6, 0, records.ids)],
            'user_id': user.id,
        })
        export.sudo().post_notification()
        return export

    @api.multi
    def post_notification(self):
        channel = self.env.ref('base_export_security.export_channel')
        field_labels = ', '.join(
            self.field_ids.mapped('field_description'),
        )
        message_data = {
            'records': len(self.record_ids),
            'model': self.model_id.name,
            'user': self.user_id.name,
            'fields': field_labels,
        }
        message_body = _(
            '%(records)d <b>%(model)s</b> records exported by <b>%(user)s'
            '</b>.<br><b>Fields exported:</b> %(fields)s'
        ) % message_data
        message = channel.message_post(
            body=message_body,
            message_type='notification',
            subtype='mail.mt_comment',
        )
        return message
