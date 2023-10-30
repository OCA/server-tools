# -*- coding: utf-8 -*-
# Copyright 2023 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Extend base adapter model for connections through http(s)."""
import json
import logging

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class ExternalSystemAdapterHTTP(models.AbstractModel):
    """HTTP external system Adapter"""

    _inherit = "external.system.adapter"
    _name = "external.system.adapter.http"
    _description = __doc__

    @api.model
    def external_get_client(self):
        """Return self as the client."""
        return self

    @api.model
    def external_destroy_client(self, client):
        """If needed logout of server."""
        pass

    def get(self, endpoint=None, params=None, **kwargs):
        """Pass transparantly to request.get, but check response."""
        url = self._get_url(endpoint=endpoint)
        _logger.debug("Will get data from %s", url)
        response = requests.get(url, params=params, **kwargs)
        if response.status_code != 200:
            message = _("Data could not be retrieved from endpoint %s: %s") % (
                endpoint,
                str(response.text),
            )
            _logger.error(message)
            raise UserError(message)
        _logger.info(
            _("Data succesfully retrieved from endpoint %s"),
            endpoint,
        )
        return response

    def post(self, endpoint=None, data=None, json=None, **kwargs):
        """Post data to http server."""
        url = self._get_url(endpoint=endpoint)
        _logger.debug("Will post data to %s", url)
        response = requests.post(url, data=data, json=json, **kwargs)
        if response.status_code not in (200, 201):
            message = _("Data could not be pushed to endpoint %s: %s") % (
                endpoint,
                str(response.text),
            )
            _logger.error(message)
            raise UserError(message)

    def _get_url(self, endpoint=None, url_suffix=None):
        """Make full url for endpoint.

        The configured remote_path, endpoint and the passed url_suffix
        must, if used, always start with "/".
        """
        system = self.system_id
        if endpoint:
            endpoint_model = self.env["external.system.endpoint"]
            endpoint_record = endpoint_model.search(
                [
                    ("system_id", "=", system.id),
                    ("name", "=", endpoint),
                ],
                limit=1
            )
            if not endpoint_record:
                raise UserError(
                    _("Endpoint %s not found on system %s")
                    % (endpoint, system.name)
                )
        url = "%(scheme)s://%(host)s%(port)s%(remote_path)s%(endpoint)s%(url_suffix)s" % {
            "scheme": system.scheme or "https",
            "host": system.host,
            "port": ":" + str(system.port) if system.port else "",
            "remote_path": system.remote_path if system.remote_path else "",
            "endpoint": endpoint_record.endpoint if endpoint else "",
            "url_suffix": url_suffix if url_suffix else "",
        }
        return url
