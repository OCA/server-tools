# -*- encoding: utf-8 -*-
##############################################################################
#
#    Admin Passkey module for OpenERP
#    Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models


class base_config_settings(models.TransientModel):
    _inherit = 'base.config.settings'

    # Getter / Setter Section
    @api.model
    def get_default_auth_admin_passkey_send_to_admin(self, fields):
        return {
            'auth_admin_passkey_send_to_admin':
            self.env["ir.config_parameter"].get_param(
                "auth_admin_passkey.send_to_admin")
        }

    @api.multi
    def set_auth_admin_passkey_send_to_admin(self):
        for config in self:
            self.env['ir.config_parameter'].set_param(
                "auth_admin_passkey.send_to_admin",
                config.auth_admin_passkey_send_to_admin or '')

    @api.model
    def get_default_auth_admin_passkey_send_to_user(self, fields):
        return {
            'auth_admin_passkey_send_to_user':
            self.env["ir.config_parameter"].get_param(
                "auth_admin_passkey.send_to_user")
        }

    @api.multi
    def set_auth_admin_passkey_send_to_user(self):
        for config in self:
            self.env['ir.config_parameter'].set_param(
                "auth_admin_passkey.send_to_user",
                config.auth_admin_passkey_send_to_user or '')

    auth_admin_passkey_send_to_admin = fields.Boolean(
        string='Send email to admin user.',
        help="""When the administrator use his password to login in """
             """with a different account, OpenERP will send an email """
             """to the admin user.""")

    auth_admin_passkey_send_to_user = fields.Boolean(
        string='Send email to user.',
        help="""When the administrator use his password to login in """
             """with a different account, OpenERP will send an email """
             """to the account user.""")
