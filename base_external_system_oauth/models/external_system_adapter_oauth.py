# Copyright 2023-2024 Therp BV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=no-member
"""Extend external system with oauth authentication."""
import logging

from odoo import _, models
from odoo.exceptions import UserError

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def strip_empty(data):
    """Strip all empty data from nested datastructure."""
    if isinstance(data, dict):
        return {k: strip_empty(v) for k, v in data.items() if k and v}
    if isinstance(data, list):
        return [strip_empty(item) for item in data if item]
    if isinstance(data, tuple):
        return tuple(strip_empty(item) for item in data if item)
    if isinstance(data, set):
        return {strip_empty(item) for item in data if item}
    return strip_empty_spaces(data)


def strip_empty_spaces(string):
    """Remove all whitespace from end of string like item."""
    if isinstance(string, str):
        return string.strip()
    return string


class ExternalSystemAdapterOAuth(models.AbstractModel):
    """This is an Interface implementing the OAuth module."""

    _name = "external.system.adapter.oauth"
    _inherit = "external.system.adapter.http"
    _description = "External System Adapter OAuth"

    def get_token(self):
        """Get token from adapter_memory."""
        return self.env.context["adapter_memory"].get("token", None)

    def set_token(self, value):
        """Store token in adapter_memor."""
        self.env.context["adapter_memory"]["token"] = value

    def del_token(self):
        """Get system from environment."""
        if "token" in self.env.context["adapter_memory"]:
            del self.env.context["adapter_memory"]["token"]

    token = property(get_token, set_token, del_token)

    def external_get_client(self):
        """Return token that can be used to access remote system."""
        client = super(ExternalSystemAdapterOAuth, self).external_get_client()
        oauth = self.system_id.oauth_definition_id
        self.token = oauth.get_access_token()
        return client

    def external_destroy_client(self, client):
        """Delete token from client."""
        del self.token
        return super(ExternalSystemAdapterOAuth, self).external_destroy_client(client)

    def post(self, endpoint=None, data=None, json=None, **kwargs):
        """Send post request."""
        headers = kwargs.pop("headers", {})
        self._set_oauth_headers(headers)
        return super(ExternalSystemAdapterOAuth, self).post(
            endpoint=endpoint, data=data, json=json, headers=headers, **kwargs
        )

    def get_json(self, endpoint=None, params=None, **kwargs):
        """Get json formatted data from remote system."""
        self._set_oauth_headers(**kwargs)
        return super(ExternalSystemAdapterOAuth, self).get(
            endpoint=endpoint, params=params, **kwargs
        )

    def _set_oauth_headers(self, headers):
        """Set headers in keyword arguments."""
        self._check_token()
        headers["Content-Type"] = "application/json"
        self._add_authorization_header(headers)

    def _check_token(self):
        """Check for connection authorization (we have a token)."""
        if not self.token:
            raise UserError(_("Not connected to external system %s.") % self.name)

    def _add_authorization_header(self, headers):
        """Add authorization header to the passed headers dictionary."""
        headers["Authorization"] = "Bearer %(token)s" % {"token": self.token}

    def strip_empty_data(self, data):
        """ "Utility method that can be called on adapter to cleanup data."""
        return strip_empty(data)
