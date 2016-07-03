# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class BaseEncryptedFieldGetPassphrase(models.AbstractModel):
    _name = 'base.encrypted.field.get.passphrase'
    _inherit = 'base.encrypted.field.noop.wizard'
    _description = 'Fill in the passphrase for your PGP key'

    passphrase = fields.Char(required=True)
