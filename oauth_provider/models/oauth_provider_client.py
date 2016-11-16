# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import uuid
import logging
from openerp import models, api, fields
from ..oauth2.validator import OdooValidator

_logger = logging.getLogger(__name__)

try:
    from oauthlib import oauth2
except ImportError:
    _logger.debug('Cannot `import oauthlib`.')


class OAuthProviderClient(models.Model):
    _name = 'oauth.provider.client'
    _description = 'OAuth Provider Client'

    name = fields.Char(required=True, help='Name of this client.')
    identifier = fields.Char(
        string='Client Identifier', required=True, readonly=True,
        default=lambda self: str(uuid.uuid4()), copy=False,
        help='Unique identifier of the client.')
    secret = fields.Char(
        help='Optional secret used to authenticate the client.')
    skip_authorization = fields.Boolean(
        help='Check this box if the user shouldn\'t be prompted to authorize '
        'or not the requested scopes.')
    application_type = fields.Selection(
        selection=[
            ('web application', 'Web Application'),
            ('mobile application', 'Mobile Application'),
            ('legacy application', 'Legacy Application'),
            ('backend application', 'Backend Application (not implemented)'),
        ], required=True, default='web application',
        help='Application type to be used with this client.')
    grant_type = fields.Selection(
        selection=[
            ('authorization_code', 'Authorization Code'),
            ('implicit', 'Implicit'),
            ('password', 'Password'),
            ('client_credentials', 'Client Credentials'),
        ], string='OAuth Grant Type',
        compute='_compute_grant_response_type', store=True,
        help='Grant type used by the client for OAuth.')
    response_type = fields.Selection(
        selection=[
            ('code', 'Authorization Code'),
            ('token', 'Token'),
            ('none', 'None'),
        ], string='OAuth Response Type',
        compute='_compute_grant_response_type', store=True,
        help='Response type used by the client for OAuth.')
    token_type = fields.Selection(
        selection=[('random', 'Randomly generated')],
        required=True, default='random',
        help='Type of token to return. The base module only provides randomly '
        'generated tokens.')
    scope_ids = fields.Many2many(
        comodel_name='oauth.provider.scope', string='Allowed Scopes',
        help='List of scopes the client is allowed to access.')
    redirect_uri_ids = fields.One2many(
        comodel_name='oauth.provider.redirect.uri', inverse_name='client_id',
        string='OAuth Redirect URIs',
        help='Allowed redirect URIs for the client.')

    _sql_constraints = [
        ('identifier_unique', 'UNIQUE (identifier)',
         'The identifier of the client must be unique !'),
    ]

    @api.model
    def application_type_mapping(self):
        return {
            'web application': ('authorization_code', 'code'),
            'mobile application': ('implicit', 'token'),
            'legacy application': ('password', 'none'),
            'backend application': ('client_credentials', 'none'),
        }

    @api.multi
    @api.depends('application_type')
    def _compute_grant_response_type(self):
        applications = self.application_type_mapping()
        for client in self:
            client.grant_type, client.response_type = applications[
                client.application_type]

    @api.multi
    def get_oauth2_server(self, validator=None, **kwargs):
        """ Returns an OAuth2 server instance, depending on the client application type

        Generates an OdooValidator instance if no custom validator is defined
        All other arguments are directly passed to the server constructor (for
        example, a token generator function)
        """
        self.ensure_one()

        if validator is None:
            validator = OdooValidator()

        if self.application_type == 'web application':
            return oauth2.WebApplicationServer(validator, **kwargs)
        elif self.application_type == 'mobile application':
            return oauth2.MobileApplicationServer(validator, **kwargs)
        elif self.application_type == 'legacy application':
            return oauth2.LegacyApplicationServer(validator, **kwargs)
        elif self.application_type == 'backend application':
            return oauth2.BackendApplicationServer(validator, **kwargs)

    @api.multi
    def generate_user_id(self, user):
        """ Generates a unique user identifier for this client

        Include the client and user identifiers in the final identifier to
        generate a different identifier for the same user, depending on the
        client accessing this user. By doing this, clients cannot find a list
        of common users by comparing their identifiers list from tokeninfo.
        """
        self.ensure_one()

        user_identifier = self.identifier \
            + user.sudo().oauth_identifier

        # Use a sha256 to avoid a too long final string
        return hashlib.sha256(user_identifier).hexdigest()
