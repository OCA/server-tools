# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class BaseEncryptedFieldSelectOrCreateGroup(models.AbstractModel):
    _name = 'base.encrypted.field.select.or.create.group'
    _inherit = 'base.encrypted.field.noop.wizard'
    _description = 'Select or create encryption group'

    encryption_group_id = fields.Many2one(
        'encryption.group', string='Existing group',
        domain=lambda self: [
            ('encrypted_field_user_ids.user_id', '=', self.env.user.id),
        ])
    new_name = fields.Char('Create new group with name')
    new_member_ids = fields.Many2many(
        'res.users', string='Other members',
        domain=lambda self: [
            ('pgp_public_key', '!=', False),
            ('id', '!=', self.env.user.id),
        ])
