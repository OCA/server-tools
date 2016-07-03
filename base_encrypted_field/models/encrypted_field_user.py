# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class EncryptedFieldUser(models.Model):
    _name = 'encrypted.field.user'
    _description = 'User accessing encrypted fields'

    encryption_group_id = fields.Many2one(
        'encryption.group', string='Encryption group', required=True,
        ondelete='restrict')
    user_id = fields.Many2one(
        'res.users', string='User', required=True, ondelete='cascade')
    key = fields.Text('Key', required=True)
