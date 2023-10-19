# Copyright 2020 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=no-self-use
"""Provide extra functionality to use Microsoft oauth for applications."""
import logging

import requests
from requests.auth import HTTPBasicAuth

from odoo import fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class AuthOAuthProvider(models.Model):
    """Abstract model to communicate with oauth authentication provider."""

    _inherit = "auth.oauth.provider"

    tenant_id = fields.Char()
    client_secret = fields.Char()
    provider_type = fields.Selection(
        selection=[
            ("basic", "Use client_id and client_secret for basic Authentication"),
            ("microsoft_client_secret", "Microsoft Client Secret autehntication"),
        ],
        default="basic",
        help="Provider type determines the method to retrieve bearer token",
    )

    def action_test_get_token(self):
        """Test wether we can get token using this configuration."""
        self.get_access_token()

    def get_access_token(self):
        """Redirect to method specific to provider type."""
        self.ensure_one()
        handler = getattr(self, "_get_access_token_" + self.provider_type)
        return handler()

    def _get_access_token_basic(self):
        """Get access token using basic authentication."""
        login_params = {
            "grant_type": "client_credentials",
        }
        basic = HTTPBasicAuth(self.client_id, self.client_secret)
        response = requests.post(
            url=self.auth_endpoint, params=login_params, auth=basic
        )
        self._check_response(response)
        return response.json()["access_token"]

    def _get_access_token_microsoft_client_secret(self):
        """Get access token from Microsoft."""
        login_url = "%(auth_endpoint)s/%(tenant_id)s%(validation_endpoint)s" % {
            "auth_endpoint": self.auth_endpoint,
            "tenant_id": self.tenant_id,
            "validation_endpoint": self.validation_endpoint,
        }
        scope = self.scope % self.client_id
        login_params = {
            "client_id": self.client_id,
            "scope": scope,
            "tenant": self.tenant_id,
            "grant_type": "client_credentials",
            "client_secret": self.client_secret,
        }
        login_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(
            url=login_url, headers=login_headers, data=login_params
        )
        self._check_response(response)
        return response.json()["access_token"]

    def _check_response(self, response):
        """Check response from oauth provider."""
        if response.status_code != 200:
            raise UserError(
                "Error at login to OAuth provider:\n"
                "Status_code: %(status_code)s\n"
                "Response: %(response)s"
                % {"status_code": response.status_code, "response": response.content}
            )
        _logger.debug(
            "Oauth status_code %s, response content %s",
            response.status_code,
            response.content,
        )
