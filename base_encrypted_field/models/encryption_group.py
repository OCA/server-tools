# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class EncryptionGroup(models.Model):
    _name = 'encryption.group'
    _description = 'Encryption group'

    name = fields.Char('Name', required=True)
    encrypted_field_ids = fields.One2many(
        'encrypted.field', 'encryption_group_id', string='Encrypted fields')
    encrypted_field_user_ids = fields.One2many(
        'encrypted.field.user', 'encryption_group_id', string='Users')

    @api.model
    def update_encrypted_fields(self, encrypted_fields):
        import pdb
        pdb.set_trace()
        for field_spec in encrypted_fields:
            field = self.env['encrypted.field'].search([
                ('field_id.name', '=', field_spec['field']),
                ('field_id.model_id.model', '=', field_spec['res_model']),
            ])
            if not field:
                field = self.env['encrypted.field'].create({
                    'encryption_group_id': field_spec['group_id'],
                    'field_id': self.env['ir.model.fields'].search([
                        ('name', '=', field_spec['field']),
                        ('model_id.model', '=', field_spec['res_model']),
                    ]).id,
                })
            if field.encrypted_record_ids.filtered(
                lambda x: x.res_id == field_spec['res_id']
            ):
                continue
            field.write({
                'encrypted_record_ids': [
                    (0, 0, {'res_id': field_spec['res_id']}),
                ],
            })
