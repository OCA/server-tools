# -*- coding: utf-8 -*-
# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import openerp.exceptions
from openerp.addons.auth_from_http_remote_user import utils


class ResUsers(models.Model):
    _inherit = 'res.users'

    sso_key = fields.Char(
        'SSO Key', size=utils.KEY_LENGTH, readonly=True, copy=False)

    @api.model
    def check_credentials(self, password):
        try:
            return super(ResUsers, self).check_credentials(password)
        except openerp.exceptions.AccessDenied:
            res = self.sudo().search([('id', '=', self.env.uid),
                                      ('sso_key', '=', password)])
            if not res:
                raise
