# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class EncryptedField(models.Model):
    _name = 'encrypted.field'
    _description = 'Encrypted field'

    encryption_group_id = fields.Many2one(
        'encryption.group', string='Encryption group', required=True,
        ondelete='restrict')
    field_id = fields.Many2one(
        'ir.model.fields', string='Field', required=True, ondelete='cascade')
    encrypted_record_ids = fields.One2many(
        'encrypted.record', 'encrypted_field_id', string='Encrypted records')
