# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
from .common_test_controller import OAuthProviderControllerTransactionCase
from .common_test_oauth_provider_controller import \
    TestOAuthProviderRefreshTokenController, \
    TestOAuthProviderAurhorizeController, \
    TestOAuthProviderTokeninfoController, \
    TestOAuthProviderUserinfoController, \
    TestOAuthProviderOtherinfoController, \
    TestOAuthProviderRevokeTokenController

_logger = logging.getLogger(__name__)

try:
    import oauthlib
except ImportError:
    _logger.debug('Cannot `import oauthlib`.')


class TestOAuthProviderController(
        OAuthProviderControllerTransactionCase,
        TestOAuthProviderRefreshTokenController,
        TestOAuthProviderAurhorizeController,
        TestOAuthProviderTokeninfoController,
        TestOAuthProviderUserinfoController,
        TestOAuthProviderOtherinfoController,
        TestOAuthProviderRevokeTokenController):
    def setUp(self):
        super(TestOAuthProviderController, self).setUp('web application')

    def new_code(self):
        # Configure the client to skip the authorization page
        self.client.skip_authorization = True

        # Call the authorize method with good values
        state = 'Some custom state'
        self.login('demo', 'demo')
        response = self.get_request('/oauth2/authorize', data={
            'client_id': self.client.identifier,
            'response_type': self.client.response_type,
            'redirect_uri': self.redirect_uri_base,
            'scope': self.client.scope_ids[0].code,
            'state': state,
        })
        # A new authorization code should have been generated
        # We can safely pick the latest generated code here, because no other
        # code could have been generated during the test
        code = self.env['oauth.provider.authorization.code'].search([
            ('client_id', '=', self.client.id),
        ], order='id DESC', limit=1)
        # The response should be a redirect to the redirect URI, with the
        # authorization_code added as GET parameter
        self.assertEqual(response.status_code, 302)
        query_string = oauthlib.common.urlencode(
            {'state': state, 'code': code.code}.items())
        self.assertEqual(
            response.headers['Location'], '{uri_base}?{query_string}'.format(
                uri_base=self.redirect_uri_base, query_string=query_string))
        self.assertEqual(code.user_id, self.user)

        self.logout()

        return code

    def test_token_error_missing_session(self):
        """ Check /oauth2/token without any session set

        Must return an invalid_client_id error
        """
        response = self.post_request('/oauth2/token')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client_id'})

    def test_token_error_missing_arguments(self):
        """ Check /oauth2/token without any argument

        Must return an invalid_client_id error
        """
        # Generate an authorization code to set the session
        self.new_code()

        response = self.post_request('/oauth2/token')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client_id'})

    def test_token_error_wrong_grant_type(self):
        """ Check /oauth2/token with an invalid grant type

        Must return an invalid_client_id error
        """
        # Generate an authorization code to set the session
        self.new_code()

        response = self.post_request('/oauth2/token', data={
            'grant_type': 'Wrong grant type',
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client_id'})

    def test_token_error_missing_code(self):
        """ Check /oauth2/token without code

        Must return an invalid_client_id error
        """
        # Generate an authorization code to set the session
        self.new_code()

        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client_id'})

    def test_token_error_missing_client_id(self):
        """ Check /oauth2/token without client

        Must return an invalid_client_id error
        """
        # Generate an authorization code to set the session
        self.new_code()

        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
            'code': 'Wrong code',
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client_id'})

    def test_token_error_wrong_client_identifier(self):
        """ Check /oauth2/token with a wrong client identifier

        Must return an invalid_client_id error
        """
        # Generate an authorization code to set the session
        self.new_code()

        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
            'client_id': 'Wrong client identifier',
            'code': 'Wrong code',
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client_id'})

    def test_token_error_wrong_code(self):
        """ Check /oauth2/token with a wrong code

        Must return an invalid_grant error
        """
        # Generate an authorization code to set the session
        self.new_code()

        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
            'client_id': self.client.identifier,
            'code': 'Wrong code',
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.data), {'error': 'invalid_grant'})

    def test_token_error_missing_redirect_uri(self):
        """ Check /oauth2/token without redirect_uri

        Must return an access_denied error
        """
        # Generate an authorization code
        code = self.new_code()

        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
            'client_id': self.client.identifier,
            'code': code.code,
        })
        # Two possible returned errors, depending on the oauthlib version
        self.assertIn(response.status_code, (400, 401))
        if response.status_code == 400:
            self.assertEqual(json.loads(response.data), {
                'error': 'invalid_request',
                'error_description': 'Mismatching redirect URI.',
            })
        else:
            self.assertEqual(
                json.loads(response.data), {'error': 'access_denied'})

    def test_token_error_wrong_redirect_uri(self):
        """ Check /oauth2/token with a wrong redirect_uri

        Must return an access_denied error
        """
        # Generate an authorization code
        code = self.new_code()

        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
            'client_id': self.client.identifier,
            'code': code.code,
            'redirect_uri': 'Wrong redirect URI',
        })
        # Two possible returned errors, depending on the oauthlib version
        self.assertIn(response.status_code, (400, 401))
        if response.status_code == 400:
            self.assertEqual(json.loads(response.data), {
                'error': 'invalid_request',
                'error_description': 'Mismatching redirect URI.',
            })
        else:
            self.assertEqual(
                json.loads(response.data), {'error': 'access_denied'})

    def test_token_error_wrong_client_id(self):
        """ Check /oauth2/token with a wrong client id

        Must return an invalid_client_id error
        """
        # Generate an authorization code
        code = self.new_code()

        response = self.post_request('/oauth2/token', data={
            'grant_type': self.client.grant_type,
            'client_id': 'Wrong client id',
            'code': code.code,
            'redirect_uri': self.redirect_uri_base,
            'scope': self.client.scope_ids[0].code,
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client_id'})

    def test_token_error_missing_refresh_token(self):
        """ Check /oauth2/token in refresh token mode without refresh token

        Must return an invalid_request error
        """
        # Generate an authorization code to set the session
        self.new_code()

        response = self.post_request('/oauth2/token', data={
            'grant_type': 'refresh_token',
            'client_id': self.client.identifier,
            'redirect_uri': self.redirect_uri_base,
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
        # Generate an authorization code to set the session
        self.new_code()

        response = self.post_request('/oauth2/token', data={
            'grant_type': 'refresh_token',
            'client_id': self.client.identifier,
            'redirect_uri': self.redirect_uri_base,
            'scope': self.client.scope_ids[0].code,
            'refresh_token': 'Wrong refresh token',
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.data), {'error': 'invalid_grant'})

    def test_authorize_skip_authorization(self):
        """ Call /oauth2/authorize while skipping the authorization page """
        # Configure the client to skip the authorization page
        self.client.skip_authorization = True

        # Call the authorize method with good values
        state = 'Some custom state'
        self.login('demo', 'demo')
        response = self.get_request('/oauth2/authorize', data={
            'client_id': self.client.identifier,
            'response_type': self.client.response_type,
            'redirect_uri': self.redirect_uri_base,
            'scope': self.client.scope_ids[0].code,
            'state': state,
        })
        # A new authorization code should have been generated
        # We can safely pick the latest generated code here, because no other
        # code could have been generated during the test
        code = self.env['oauth.provider.authorization.code'].search([
            ('client_id', '=', self.client.id),
        ], order='id DESC', limit=1)
        # The response should be a redirect to the redirect URI, with the
        # authorization_code added as GET parameter
        self.assertEqual(response.status_code, 302)
        query_string = oauthlib.common.urlencode({
            'state': state,
            'code': code.code,
        }.items())
        self.assertEqual(
            response.headers['Location'], '{uri_base}?{query_string}'.format(
                uri_base=self.redirect_uri_base, query_string=query_string))
        self.assertEqual(code.user_id, self.user)

    def test_successful_token_retrieval(self):
        """ Check the full process for a WebApplication

        GET, then POST, token and informations retrieval
        """
        # Call the authorize method with good values to fill the session scopes
        # and credentials variables
        state = 'Some custom state'
        self.login('demo', 'demo')
        response = self.get_request('/oauth2/authorize', data={
            'client_id': self.client.identifier,
            'response_type': self.client.response_type,
            'redirect_uri': self.redirect_uri_base,
            'scope': self.client.scope_ids[0].code,
            'state': state,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.name in response.data)
        self.assertTrue(self.client.scope_ids[0].name in response.data)
        self.assertTrue(self.client.scope_ids[0].description in response.data)

        # Then, call the POST route to validate the authorization
        response = self.post_request('/oauth2/authorize')
        # A new authorization code should have been generated
        # We can safely pick the latest generated code here, because no other
        # code could have been generated during the test
        code = self.env['oauth.provider.authorization.code'].search([
            ('client_id', '=', self.client.id),
        ], order='id DESC', limit=1)
        # The response should be a redirect to the redirect URI, with the
        # authorization_code added as GET parameter
        self.assertEqual(response.status_code, 302)
        query_string = oauthlib.common.urlencode({
            'state': state,
            'code': code.code,
        }.items())
        self.assertEqual(
            response.headers['Location'], '{uri_base}?{query_string}'.format(
                uri_base=self.redirect_uri_base, query_string=query_string))
        self.assertEqual(code.user_id, self.user)

        self.logout()

        # Now that the user vaidated the authorization, we can ask for a token,
        # using the returned code
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'redirect_uri': self.redirect_uri_base,
            'scope': self.client.scope_ids[0].code,
            'code': code.code,
            'grant_type': self.client.grant_type,
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
        self.assertEqual(token.scope_ids, code.scope_ids)
        self.assertEqual(token.user_id, self.user)
