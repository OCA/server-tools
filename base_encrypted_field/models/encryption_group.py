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
        # TODO: why not inject this into BaseModel?
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

    @api.model
    def get_encrypted_fields(self, res_model, res_id, fields_list=None):
        # TODO: why not inject this into BaseModel?
        result = []
        for field_name, field_desc in self.env[res_model].fields_get(
            allfields=fields_list
        ).iteritems():
            if not field_desc.get('encryptable'):
                continue
            encrypted_field = self.env['encrypted.field'].search([
                ('field_id.name', '=', field_name),
                ('field_id.model_id.model', '=', res_model),
                ('encrypted_record_ids.res_id', '=', res_id),
            ])
            if not encrypted_field:
                continue
            result.append({
                'field': field_name,
                'group_id': encrypted_field.encryption_group_id.id,
                'encrypted_passphrase': encrypted_field.encryption_group_id
                .encrypted_field_user_ids.filtered(
                    lambda x: x.user_id == self.env.user
                ).key
            })
        return result
