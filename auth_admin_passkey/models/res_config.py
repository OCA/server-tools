# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class BaseConfigSettings(models.TransientModel):
    _inherit = "base.config.settings"

    # Getter / Setter Section
    @api.model
    def get_default_auth_admin_passkey_send_to_admin(self, fields):
        return {
            "auth_admin_passkey_send_to_admin": safe_eval(
                self.env["ir.config_parameter"].get_param(
                    "auth_admin_passkey.send_to_admin"
                )
                or "False"
            )
        }

    @api.multi
    def set_auth_admin_passkey_send_to_admin(self):
        for config in self:
            self.env["ir.config_parameter"].set_param(
                "auth_admin_passkey.send_to_admin",
                str(config.auth_admin_passkey_send_to_admin),
            )

    @api.model
    def get_default_auth_admin_passkey_send_to_user(self, fields):
        return {
            "auth_admin_passkey_send_to_user": safe_eval(
                self.env["ir.config_parameter"].get_param(
                    "auth_admin_passkey.send_to_user"
                )
                or "False"
            )
        }

    @api.multi
    def set_auth_admin_passkey_send_to_user(self):
        for config in self:
            self.env["ir.config_parameter"].set_param(
                "auth_admin_passkey.send_to_user",
                str(config.auth_admin_passkey_send_to_user),
            )

    auth_admin_passkey_send_to_admin = fields.Boolean(
        string="Send email to admin user.",
        help="When the administrator use his password to login in "
        "with a different account, Odoo will send an email "
        "to the admin user.",
    )

    auth_admin_passkey_send_to_user = fields.Boolean(
        string="Send email to user.",
        help="When the administrator use his password to login in "
        "with a different account, Odoo will send an email "
        "to the account user.",
    )
