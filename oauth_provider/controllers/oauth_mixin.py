# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import http
from odoo.addons.web.controllers.main import ensure_db

from ..exceptions import OauthApiException, OauthInvalidTokenException
from ..http import _json_response


_logger = logging.getLogger(__name__)

try:
    import oauthlib
except ImportError:
    _logger.debug('Cannot `import oauthlib`.')


class OauthMixin(http.Controller):

    def _validate_model(self, model_name, token=None):
        """ Validate the access token & return a usable model.

        Args:
            model_name (str): Name of model to find.
            token (OauthProviderToken, optional): Will return the model in
                the scope of the token user, if defined.

        Returns:
            IrModel: Usable model object that matched model_name.

        Raises:
            OauthApiException: If the model is not found.
        """
        ensure_db()
        model_obj = http.request.env['ir.model'].search([
            ('model', '=', model_name),
        ])
        if not model_obj:
            raise OauthApiException('Model Not Found')
        if token is not None:
            model_obj = model_obj.sudo(user=token.user_id)
        return model_obj

    def _validate_token(self, access_token):
        """ Find the access token & return it if valid.

        Args:
            access_token (str): Access token that should be validated.

        Returns:
            OAuthProviderToken: Token record, if valid.

        Raises:
            OauthInvalidTokenException: When the token is invalid or expired.
        """
        ensure_db()
        token = self._get_access_token(access_token)
        if not token:
            raise OauthInvalidTokenException()
        return token

    @classmethod
    def _get_access_token(cls, access_token):
        """ Verify access token and return record if valid.

        Args:
             access_token (str): OAuth2 access token to be validated.

        Returns:
            OauthProviderToken: Valid token record for use.
            NoneType: None if no matching token was found in the database.
            bool: False if the token was invalid.
        """
        token = http.request.env['oauth.provider.token'].search([
            ('token', '=', access_token),
        ])
        if not token:
            return None

        oauth2_server = token.client_id.get_oauth2_server()
        # Retrieve needed arguments for oauthlib methods
        uri, http_method, body, headers = cls._get_request_information()

        # Validate request information
        valid, oauthlib_request = oauth2_server.verify_request(
            uri, http_method=http_method, body=body, headers=headers,
        )

        if valid:
            return token

        return False

    @staticmethod
    def _get_request_information():
        """ Retrieve needed arguments for oauthlib methods.

        Returns:
            tuple: uri, http_method, body, headers
        """
        uri = http.request.httprequest.base_url
        http_method = http.request.httprequest.method
        body = oauthlib.common.urlencode(
            http.request.httprequest.values.items(),
        )
        headers = http.request.httprequest.headers

        return uri, http_method, body, headers

    @staticmethod
    def _json_response(data=None, error=None, headers=None, status=None):
        """ Returns a json response to the client.

        Args:
            result (mixed, optional): User's requested data.
            error (dict, optional): Serialized error data (from
                `_handle_exception`).
            headers (dict, optional): Mapping of headers to apply to the
                request. If the `Content-Type` header is not defined,
                 `application/json` will automatically be added.

        Returns:
            Response: Werkzeug response object based on the input.
        """
        try:
            return http.request._json_response(data, error)
        except AttributeError:
            return _json_response(data, error, headers, status)
