# -*- coding: utf-8 -*-
# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import AccessDenied
from threading import current_thread


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        # Check if the remote is banned when login with oauth provider
        oauth_uid = validation['user_id']
        oauth_user = self.search([
            ("oauth_uid", "=", oauth_uid),
            ('oauth_provider_id', '=', provider)]
        )
        if oauth_user:
            try:
                remote_addr = current_thread().environ["REMOTE_ADDR"]
            except (KeyError, AttributeError):
                remote_addr = False
            # Fail if the remote is banned
            trusted = self.env["res.authentication.attempt"]._trusted(
                remote_addr,
                oauth_user.login,
            )
            if not trusted:
                raise AccessDenied
        return super(ResUsers, self)._auth_oauth_signin(
            provider,
            validation,
            params
        )
