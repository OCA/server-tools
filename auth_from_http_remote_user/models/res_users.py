# -*- coding: utf-8 -*-
# Copyright 2014-2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import AccessDenied
from .. import utils


class ResUsers(models.Model):
    _inherit = 'res.users'

    sso_key = fields.Char(
        'SSO Key', size=utils.KEY_LENGTH, readonly=True, copy=False)

    @api.model
    def check_credentials(self, password):
        try:
            return super(ResUsers, self).check_credentials(password)
        except AccessDenied:
            res = self.sudo().search([('id', '=', self.env.uid),
                                      ('sso_key', '=', password)])
            if not res:
                raise
