# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    pgp_private_key = fields.Text('Private pgp key', readonly=True)
    pgp_public_key = fields.Text('Public pgp key', readonly=True)
