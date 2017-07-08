# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging
from datetime import datetime, timedelta
from openerp import http
from openerp import fields

_logger = logging.getLogger(__name__)

try:
    from oauthlib.oauth2 import RequestValidator
except ImportError:
    _logger.debug('Cannot `import oauthlib`.')


class OdooValidator(RequestValidator):
    """ OAuth2 validator to be used in Odoo

    This is an implementation of oauthlib's RequestValidator interface
    https://github.com/idan/oauthlib/oauthlib/oauth2/rfc6749/request_validator.py
    """
    def _load_client(self, request, client_id=None):
        """ Returns a client instance for the request """
        client = request.client
        if not client:
            request.client = http.request.env['oauth.provider.client'].search([
                ('identifier', '=', client_id or request.client_id),
            ])
            request.odoo_user = http.request.env.user
            request.client.client_id = request.client.identifier

    def _extract_auth(self, request):
        """ Extract auth string from request headers """
        auth = request.headers.get('Authorization', ' ')
        auth_type, auth_string = auth.split(' ', 1)
        if auth_type != 'Basic':
            return ''

        return auth_string

    def authenticate_client(self, request, *args, **kwargs):
        """ Authenticate the client """
        auth_string = self._extract_auth(request)
        auth_string_decoded = base64.b64decode(auth_string)

        # If we don't have a proper auth string, get values in the request body
        if ':' not in auth_string_decoded:
            client_id = request.client_id
            client_secret = request.client_secret
        else:
            client_id, client_secret = auth_string_decoded.split(':', 1)

        self._load_client(request)
        return (request.client.identifier == client_id) and \
            (request.client.secret or '') == (client_secret or '')

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        """ Ensure client_id belong to a non-confidential client """
        self._load_client(request, client_id=client_id)
        return bool(request.client) and not request.client.secret

    def client_authentication_required(self, request, *args, **kwargs):
        """ Determine if the client authentication is required for the request
        """
        # If an auth string was specified, unconditionnally authenticate
        if self._extract_auth(request):
            return True

        self._load_client(request)
        return request.client.grant_type in (
            'password',
            'authorization_code',
            'refresh_token',
        ) or request.client_secret or \
            not request.odoo_user.active

    def confirm_redirect_uri(
            self, client_id, code, redirect_uri, client, *args, **kwargs):
        """ Ensure that the authorization process' redirect URI

        The authorization process corresponding to the code must begin by using
        this redirect_uri
        """
        code = http.request.env['oauth.provider.authorization.code'].search([
            ('client_id.identifier', '=', client_id),
            ('code', '=', code),
        ])
        return redirect_uri == code.redirect_uri_id.name

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        """ Returns the default redirect URI for the client """
        client = http.request.env['oauth.provider.client'].search([
            ('identifier', '=', client_id),
        ])
        return client.redirect_uri_ids and client.redirect_uri_ids[0].name \
            or ''

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        """ Returns a list of default scoprs for the client """
        client = http.request.env['oauth.provider.client'].search([
            ('identifier', '=', client_id),
        ])
        return ' '.join(client.scope_ids.mapped('code'))

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        """ Returns the list of scopes associated to the refresh token """
        token = http.request.env['oauth.provider.token'].search([
            ('client_id', '=', request.client.id),
            ('refresh_token', '=', refresh_token),
        ])
        return token.scope_ids.mapped('code')

    def invalidate_authorization_code(
            self, client_id, code, request, *args, **kwargs):
        """ Invalidates an authorization code """
        code = http.request.env['oauth.provider.authorization.code'].search([
            ('client_id.identifier', '=', client_id),
            ('code', '=', code),
        ])
        code.sudo().write({'active': False})

    def is_within_original_scope(
            self, request_scopes, refresh_token, request, *args, **kwargs):
        """ Check if the requested scopes are within a scope of the token """
        token = http.request.env['oauth.provider.token'].search([
            ('client_id', '=', request.client.id),
            ('refresh_token', '=', refresh_token),
        ])
        return set(request_scopes).issubset(
            set(token.scope_ids.mapped('code')))

    def revoke_token(self, token, token_type_hint, request, *args, **kwargs):
        """ Revoke an access of refresh token """
        db_token = http.request.env['oauth.provider.token'].search([
            ('token', '=', token),
        ])
        # If we revoke a full token, simply unlink it
        if db_token:
            db_token.sudo().unlink()
        # If we revoke a refresh token, empty it in the corresponding token
        else:
            db_token = http.request.env['oauth.provider.token'].search([
                ('refresh_token', '=', token),
            ])
            db_token.sudo().refresh_token = False

    def rotate_refresh_token(self, request):
        """ Determine if the refresh token has to be renewed

        Called after refreshing an access token
        Always refresh the token by default, but child classes could override
        this method to change this behaviour.
        """
        return True

    def save_authorization_code(
            self, client_id, code, request, *args, **kwargs):
        """ Store the authorization code into the database """
        redirect_uri = http.request.env['oauth.provider.redirect.uri'].search([
            ('name', '=', request.redirect_uri),
        ])
        http.request.env['oauth.provider.authorization.code'].sudo().create({
            'code': code['code'],
            'client_id': request.client.id,
            'user_id': request.odoo_user.id,
            'redirect_uri_id': redirect_uri.id,
            'scope_ids': [(6, 0, request.client.scope_ids.filtered(
                lambda record: record.code in request.scopes).ids)],
        })

    def save_bearer_token(self, token, request, *args, **kwargs):
        """ Store the bearer token into the database """
        scopes = token.get('scope', '').split()
        http.request.env['oauth.provider.token'].sudo().create({
            'token': token['access_token'],
            'token_type': token['token_type'],
            'refresh_token': token.get('refresh_token'),
            'client_id': request.client.id,
            'user_id': token.get('odoo_user_id', request.odoo_user.id),
            'scope_ids': [(6, 0, request.client.scope_ids.filtered(
                lambda record: record.code in scopes).ids)],
            'expires_at': fields.Datetime.to_string(
                datetime.now() + timedelta(seconds=token['expires_in'])),
        })
        redirect_uris = request.client.redirect_uri_ids
        return redirect_uris and redirect_uris[0].name or ''

    def validate_bearer_token(self, token, scopes, request):
        """ Ensure the supplied bearer token is valid, and allowed for the scopes
        """
        token = http.request.env['oauth.provider.token'].search([
            ('token', '=', token),
        ])
        if scopes is None:
            scopes = ''

        return set(scopes.split()).issubset(
            set(token.scope_ids.mapped('code')))

    def validate_client_id(self, client_id, request, *args, **kwargs):
        """ Ensure client_id belong to a valid and active client """
        self._load_client(request)
        return bool(request.client)

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        """ Check that the code is valid, and assigned to the given client """
        code = http.request.env['oauth.provider.authorization.code'].search([
            ('client_id.identifier', '=', client_id),
            ('code', '=', code),
        ])
        request.odoo_user = code.user_id
        return bool(code)

    def validate_grant_type(
            self, client_id, grant_type, client, request, *args, **kwargs):
        """ Ensure the client is authorized to use the requested grant_type """
        return client.identifier == client_id and grant_type in (
            client.grant_type, 'refresh_token'
        )

    def validate_redirect_uri(
            self, client_id, redirect_uri, request, *args, **kwargs):
        """ Ensure the client is allowed to use the requested redurect_uri """
        return request.client.identifier == client_id and \
            redirect_uri in request.client.mapped('redirect_uri_ids.name')

    def validate_refresh_token(
            self, refresh_token, client, request, *args, **kwargs):
        """ Ensure the refresh token is valid and associated to the client """
        token = http.request.env['oauth.provider.token'].search([
            ('client_id', '=', client.id),
            ('refresh_token', '=', refresh_token),
        ])
        return bool(token)

    def validate_response_type(
            self, client_id, response_type, client, request, *args, **kwargs):
        """ Ensure the client is allowed to use the requested response_type """
        return request.client.identifier == client_id and \
            response_type == request.client.response_type

    def validate_scopes(
            self, client_id, scopes, client, request, *args, **kwargs):
        """ Ensure the client is allowed to access all requested scopes """
        return request.client.identifier == client_id and set(scopes).issubset(
            set(request.client.mapped('scope_ids.code')))

    def validate_user(
            self, username, password, client, request, *args, **kwargs):
        """ Ensure the usernamd and password are valid """
        uid = http.request.session.authenticate(
            http.request.session.db, username, password)
        request.odoo_user = http.request.env['res.users'].browse(uid)
        return bool(uid)
