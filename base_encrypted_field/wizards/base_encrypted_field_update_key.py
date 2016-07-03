# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class BaseEncryptedFieldUpdateKey(models.AbstractModel):
    _name = 'base.encrypted.field.update.key'
    _inherit = 'base.encrypted.field.noop.wizard'
    _description = 'Update PGP key'

    user_id = fields.Many2one('res.users', string='User', required=True,
                              default=lambda self: self.env.user.id)
    passphrase = fields.Char()
    private_key = fields.Text()
    public_key = fields.Text()
