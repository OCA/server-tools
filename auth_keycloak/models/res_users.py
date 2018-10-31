# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import api, models, exceptions, _
import logging
import requests
from ..exceptions import OAuthError

logger = logging.getLogger(__name__)


# NOTE: `sub` is THE user id in keycloak
# https://www.keycloak.org/docs/latest/server_development/index.html#_action_token_anatomy  # noqa
# and you cannot change it https://stackoverflow.com/questions/46529363


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _keycloak_validate(self, provider, access_token):
        """Validate token against Keycloak."""
        logger.debug('Calling: %s' % provider.validation_endpoint)
        resp = requests.post(
            provider.validation_endpoint,
            data={'token': access_token},
            auth=(provider.client_id, provider.client_secret)
        )
        if not resp.ok:
            raise OAuthError(resp.reason)
        validation = resp.json()
        if validation.get("error"):
            raise OAuthError(validation)
        logger.debug('Validation: %s' % str(validation))
        return validation

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        """Override to use authentication headers.

        The method `_auth_oauth_rpc` is not pluggable
        as you don't have the provider there.
        """
        # `provider` is `provider_id` actually... I'm respecting orig signature
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        validation = self._keycloak_validate(oauth_provider, access_token)
        # clone keycloak ID expected by odoo into `user_id`
        validation['user_id'] = validation['sub']
        return validation

    @api.multi
    def button_push_to_keycloak(self, vals):
        """Quick action to push current users to Keycloak."""
        provider = self.env.ref(
            'auth_keycloak.default_keycloak_provider',
            raise_if_not_found=False
        )
        enabled = provider and provider.users_management_enabled
        if not enabled:
            raise exceptions.UserError(
                _('Keycloak provider not found or not configured properly.')
            )
        wiz = self.env['auth.keycloak.create.wiz'].create({
            'provider_id': provider.id,
            'user_ids': [(6, 0, self.ids)],
        })
        action = self.env.ref('auth_keycloak.keycloak_create_users').read()[0]
        action['res_id'] = wiz.id
        return action
