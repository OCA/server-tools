# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class EncryptedRecord(models.Model):
    _name = 'encrypted.record'
    _description = 'Encrypted record'

    encrypted_field_id = fields.Many2one(
        'encrypted.field', string='Field', required=True,
        ondelete='restrict')
    res_id = fields.Integer('ID', required=True)
