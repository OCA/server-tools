# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    pgp_private_key = fields.Text('Private pgp key', readonly=True)
    pgp_public_key = fields.Text('Public pgp key', readonly=True)

    @api.model
    def _base_encrypted_fields_inject_field_description(self, field_name,
                                                        field_desc):
        if field_name in ['pgp_private_key', 'pgp_public_key']:
            return
        return super(ResUsers, self)\
            ._base_encrypted_fields_inject_field_description(
                field_name, field_desc)
