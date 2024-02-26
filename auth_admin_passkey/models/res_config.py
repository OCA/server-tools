# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class BaseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_values(self):
        res = super(BaseConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        send_to_user = params.get_param('auth_admin_passkey.send_to_user', default="False")
        send_to_admin = params.get_param('auth_admin_passkey.send_to_admin', default="False")
        res.update({
            'auth_admin_passkey_send_to_user': safe_eval(send_to_user),
            'auth_admin_passkey_send_to_admin': safe_eval(send_to_admin),
        })
        return res

    @api.multi
    def set_values(self):
        self.ensure_one()
        super(BaseConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('auth_admin_passkey.send_to_user', str(self.auth_admin_passkey_send_to_user))
        params.set_param('auth_admin_passkey.send_to_admin', str(self.auth_admin_passkey_send_to_admin))

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
