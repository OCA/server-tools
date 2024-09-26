# -*- coding: utf-8 -*-
# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import AccessDenied

from odoo.addons.auth_oauth.models.res_users import ResUsers as AuthOauthResUsers
from odoo.addons.auth_brute_force.models.res_users import ResUsers as \
    AuthBruteForceResUsers


@api.model
def check_credentials(self, password):
    """This is the most important and specific auth check method.

    When we get here, it means that Odoo already checked the user exists
    in this database.

    Other auth methods usually plug here.
    """
    login = self.env.user.login
    with self._auth_attempt(login):
        # Update login, just in case we stored the UID before
        attempt = self._auth_attempt_update({"login": login})
        remote = attempt.get("remote")
        # Fail if the remote is banned
        trusted = self.env["res.authentication.attempt"]._trusted(
            remote,
            login,
        )
        if not trusted:
            error = AccessDenied()
            error.reason = "banned"
            raise error
        if self.sudo().search([
            ('id', '=', self.env.uid),
            ('oauth_access_token', '=', password)
        ]):
            return
        # Continue with other auth systems
        return super(AuthOauthResUsers, self).check_credentials(password)


@api.model
def check_credentials_void(self, password):
    return super(AuthBruteForceResUsers, self).check_credentials(password)


class ResUsersHookCheckCredentials(models.AbstractModel):
    _name = "res.users.hook.check.credentials"
    _description = "Provide hook point for check_credentials methods"

    def _register_hook(self):
        AuthOauthResUsers.check_credentials = check_credentials
        AuthBruteForceResUsers.check_credentials = check_credentials_void
        return super(ResUsersHookCheckCredentials, self)._register_hook()
