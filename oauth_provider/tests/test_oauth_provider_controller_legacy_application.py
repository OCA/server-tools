# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import json
import logging
from .common_test_controller import OAuthProviderControllerTransactionCase
from .common_test_oauth_provider_controller import \
    TestOAuthProviderRefreshTokenController, \
    TestOAuthProviderTokeninfoController, \
    TestOAuthProviderUserinfoController, \
    TestOAuthProviderOtherinfoController, \
    TestOAuthProviderRevokeTokenController

_logger = logging.getLogger(__name__)


class TestOAuthProviderController(
        OAuthProviderControllerTransactionCase,
        TestOAuthProviderRefreshTokenController,
        TestOAuthProviderTokeninfoController,
        TestOAuthProviderUserinfoController,
        TestOAuthProviderOtherinfoController,
        TestOAuthProviderRevokeTokenController):
    def setUp(self):
        super(TestOAuthProviderController, self).setUp('legacy application')

    def test_token_error_missing_arguments(self):
        """ Check /oauth2/token without any argument

        Must return an unsupported_grant_type error
        """
        response = self.post_request('/oauth2/token')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client_id'})

    def test_token_error_wrong_grant_type(self):
        """ Check /oauth2/token with an invalid grant type

        Must return an unsupported_grant_type error
        """
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'grant_type': 'Wrong grant type',
            'username': 'Wrong username',
            'password': 'Wrong password',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.data), {'error': 'unsupported_grant_type'})

    def test_token_error_missing_username(self):
        """ Check /oauth2/token without username

        Must return an invalid_request error
        """
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'grant_type': self.client.grant_type,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {
            'error': 'invalid_request',
            'error_description': 'Request is missing username parameter.',
        })

    def test_token_error_missing_password(self):
        """ Check /oauth2/token without password

        Must return an invalid_request error
        """
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'grant_type': self.client.grant_type,
            'username': 'Wrong username',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {
            'error': 'invalid_request',
            'error_description': 'Request is missing password parameter.',
        })

    def test_token_error_missing_client_id(self):
        """ Check /oauth2/token without client

        Must return an unauthorized_client error
        """
        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client_id'})

    def test_token_error_wrong_client_identifier(self):
        """ Check /oauth2/token with a wrong client identifier

        Must return an invalid_client_id error
        """
        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
            'client_id': 'Wrong client identifier',
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client_id'})

    def test_token_error_wrong_username(self):
        """ Check /oauth2/token with a wrong username

        Must return an invalid_grant error
        """
        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
            'client_id': self.client.identifier,
            'username': 'Wrong username',
            'password': 'demo',
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.data), {
            'error': 'invalid_grant',
            'error_description': 'Invalid credentials given.',
        })

    def test_token_error_wrong_password(self):
        """ Check /oauth2/token with a wrong password

        Must return an invalid_grant error
        """
        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
            'client_id': self.client.identifier,
            'username': self.user.login,
            'password': 'Wrong password',
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.data), {
            'error': 'invalid_grant',
            'error_description': 'Invalid credentials given.',
        })

    def test_token_error_wrong_client_id(self):
        """ Check /oauth2/token with a wrong client id

        Must return an invalid_client_id error
        """
        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
            'client_id': 'Wrong client id',
            'scope': self.client.scope_ids[0].code,
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client_id'})

    def test_token_error_missing_refresh_token(self):
        """ Check /oauth2/token in refresh token mode without refresh token

        Must return an invalid_request error
        """
        response = self.post_request('/oauth2/token', data={
            'grant_type': 'refresh_token',
            'client_id': self.client.identifier,
            'scope': self.client.scope_ids[0].code,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {
            'error': 'invalid_request',
            'error_description': 'Missing refresh token parameter.',
        })

    def test_token_error_invalid_refresh_token(self):
        """ Check /oauth2/token in refresh token mode with an invalid refresh token

        Must return an invalid_grant error
        """
        response = self.post_request('/oauth2/token', data={
            'grant_type': 'refresh_token',
            'client_id': self.client.identifier,
            'scope': self.client.scope_ids[0].code,
            'refresh_token': 'Wrong refresh token',
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.data), {'error': 'invalid_grant'})

    def test_token_with_missing_secret(self):
        """ Check client authentication without the secret provided

        Must return an invalid_client error
        """
        # Define a secret for the client
        self.client.secret = 'OAuth Client secret'

        # Ask a token to the server
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'scope': self.client.scope_ids[0].code,
            'grant_type': self.client.grant_type,
            'username': self.user.login,
            'password': 'demo',
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client'})

    def test_token_with_unexpected_secret(self):
        """ Check client authentication with an unexpected secret provided

        Must return an invalid_client error
        """
        # Don't define a secret for the client
        auth_string = base64.b64encode('{client.identifier}:secret'.format(
            client=self.client).encode()).decode()

        # Ask a token to the server
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'scope': self.client.scope_ids[0].code,
            'grant_type': self.client.grant_type,
            'username': self.user.login,
            'password': 'demo',
        }, headers=[(
            'Authorization',
            'Basic {auth_string}'.format(auth_string=auth_string)),
        ])
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client'})

    def test_token_with_wrong_secret(self):
        """ Check client authentication with a wrong secret

        Must return an invalid_client error
        """
        # Define a secret for the client
        self.client.secret = 'OAuth Client secret'
        auth_string = base64.b64encode('{client.identifier}:secret'.format(
            client=self.client).encode()).decode()

        # Ask a token to the server
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'scope': self.client.scope_ids[0].code,
            'grant_type': self.client.grant_type,
            'username': self.user.login,
            'password': 'demo',
        }, headers=[(
            'Authorization',
            'Basic {auth_string}'.format(auth_string=auth_string)),
        ])
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client'})

    def test_token_with_secret(self):
        """ Check client authentication from Authorization header """
        # Define a secret for the client
        self.client.secret = 'OAuth Client secret'
        auth_string = base64.b64encode(
            '{client.identifier}:{client.secret}'.format(
                client=self.client).encode()).decode()

        # Ask a token to the server
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'scope': self.client.scope_ids[0].code,
            'grant_type': self.client.grant_type,
            'username': self.user.login,
            'password': 'demo',
        }, headers=[(
            'Authorization',
            'Basic {auth_string}'.format(auth_string=auth_string)),
        ])
        response_data = json.loads(response.data)
        # A new token should have been generated
        # We can safely pick the latest generated token here, because no other
        # token could have been generated during the test
        token = self.env['oauth.provider.token'].search([
            ('client_id', '=', self.client.id),
        ], order='id DESC', limit=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(token.token, response_data['access_token'])
        self.assertEqual(token.token_type, response_data['token_type'])
        self.assertEqual(token.refresh_token, response_data['refresh_token'])
        self.assertEqual(token.scope_ids, self.client.scope_ids[0])
        self.assertEqual(token.user_id, self.user)

    def test_token_with_wrong_non_basic_authorization(self):
        """ Check client authentication with a non-Basic Authorization header

        Must generate a token : Non basic authorization headers are ignored
        """
        # Don't define a secret for the client
        auth_string = base64.b64encode('{client.identifier}:secret'.format(
            client=self.client).encode()).decode()

        # Ask a token to the server
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'scope': self.client.scope_ids[0].code,
            'grant_type': self.client.grant_type,
            'username': self.user.login,
            'password': 'demo',
        }, headers=[(
            'Authorization',
            'Digest {auth_string}'.format(auth_string=auth_string)),
        ])
        response_data = json.loads(response.data)
        # A new token should have been generated
        # We can safely pick the latest generated token here, because no other
        # token could have been generated during the test
        token = self.env['oauth.provider.token'].search([
            ('client_id', '=', self.client.id),
        ], order='id DESC', limit=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(token.token, response_data['access_token'])
        self.assertEqual(token.token_type, response_data['token_type'])
        self.assertEqual(token.refresh_token, response_data['refresh_token'])
        self.assertEqual(token.scope_ids, self.client.scope_ids[0])
        self.assertEqual(token.user_id, self.user)

    def test_token_with_right_non_basic_authorization(self):
        """ Check client authentication with a non-Basic Authorization header

        Must return an invalid_client error : Non basic authorization headers
        are ignored
        """
        # Define a secret for the client
        self.client.secret = 'OAuth Client secret'
        auth_string = base64.b64encode(
            '{client.identifier}:{client.secret}'.format(
                client=self.client).encode()).decode()

        # Ask a token to the server
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'scope': self.client.scope_ids[0].code,
            'grant_type': self.client.grant_type,
            'username': self.user.login,
            'password': 'demo',
        }, headers=[(
            'Authorization',
            'Digest {auth_string}'.format(auth_string=auth_string)),
        ])
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client'})

    def test_successful_token_retrieval(self):
        """ Check the full process for a LegacyApplication

        GET, then POST, token and informations retrieval
        """
        # Ask a token to the server
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'scope': self.client.scope_ids[0].code,
            'grant_type': self.client.grant_type,
            'username': self.user.login,
            'password': 'demo',
        })
        response_data = json.loads(response.data)
        # A new token should have been generated
        # We can safely pick the latest generated token here, because no other
        # token could have been generated during the test
        token = self.env['oauth.provider.token'].search([
            ('client_id', '=', self.client.id),
        ], order='id DESC', limit=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(token.token, response_data['access_token'])
        self.assertEqual(token.token_type, response_data['token_type'])
        self.assertEqual(token.refresh_token, response_data['refresh_token'])
        self.assertEqual(token.scope_ids, self.client.scope_ids[0])
        self.assertEqual(token.user_id, self.user)
