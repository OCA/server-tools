# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.tools import safe_eval


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    @api.model
    def get_default_auth_admin_passkey_send_to_admin(self, fields):
        icp = self.env['ir.config_parameter']
        return {
            'auth_admin_passkey_send_to_admin': safe_eval(icp.get_param(
                'auth_admin_passkey.send_to_admin', 'True')),
        }

    @api.model
    def get_default_auth_admin_passkey_send_to_user(self, fields):
        icp = self.env['ir.config_parameter']
        return {
            'auth_admin_passkey_send_to_user': safe_eval(icp.get_param(
                'auth_admin_passkey.send_to_user', 'True')),
        }

    auth_admin_passkey_send_to_admin = fields.Boolean(
        'Send email to admin user.',
        help=('When the administrator use his password to login in '
              'with a different account, Odoo will send an email '
              'to the admin user.'),
    )
    auth_admin_passkey_send_to_user = fields.Boolean(
        string='Send email to user.',
        help=('When the administrator use his password to login in '
              'with a different account, Odoo will send an email '
              'to the account user.'),
    )

    @api.multi
    def set_auth_admin_passkey_send_to_admin(self):
        self.ensure_one()

        icp = self.env['ir.config_parameter']
        icp.set_param(
            'auth_admin_passkey.send_to_admin',
            repr(self.auth_admin_passkey_send_to_admin))

    @api.multi
    def set_auth_admin_passkey_send_to_user(self):
        self.ensure_one()

        icp = self.env['ir.config_parameter']
        icp.set_param(
            'auth_admin_passkey.send_to_user',
            repr(self.auth_admin_passkey_send_to_user))
