# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from .common_test_controller import OAuthProviderControllerTransactionCase
from .common_test_oauth_provider_controller import \
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
        TestOAuthProviderAurhorizeController,
        TestOAuthProviderTokeninfoController,
        TestOAuthProviderUserinfoController,
        TestOAuthProviderOtherinfoController,
        TestOAuthProviderRevokeTokenController):
    def setUp(self):
        super(TestOAuthProviderController, self).setUp('mobile application')

    def test_authorize_skip_authorization(self):
        """ Call /oauth2/authorize while skipping the authorization page """
        # Configure the client to skip the authorization page
        self.client.skip_authorization = True

        # Login as demo user
        self.login(self.user.login, self.user.login)

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
        # A new token should have been generated
        # We can safely pick the latest generated token here, because no other
        # token could have been generated during the test
        token = self.env['oauth.provider.token'].search([
            ('client_id', '=', self.client.id),
        ], order='id DESC', limit=1)
        # The response should be a redirect to the redirect URI, with the
        # authorization_code added as GET parameter
        self.assertEqual(response.status_code, 302)
        query_string = oauthlib.common.urlencode({
            'access_token': token.token,
            'expires_in': 3600,
            'token_type': token.token_type,
            'scope': token.scope_ids.code,
            'state': state,
        }.items())
        self.assertEqual(
            response.headers['Location'], '{uri_base}#{query_string}'.format(
                uri_base=self.redirect_uri_base, query_string=query_string))
        self.assertEqual(token.user_id, self.user)

    def test_successful_token_retrieval(self):
        """ Check the full process for a MobileApplication

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
        self.assertTrue(self.client.name in str(response.data))
        self.assertTrue(self.client.scope_ids[0].name in str(response.data))
        self.assertTrue(
            self.client.scope_ids[0].description in str(response.data))

        # Then, call the POST route to validate the authorization
        response = self.post_request('/oauth2/authorize')
        # A new token should have been generated
        # We can safely pick the latest generated token here, because no other
        # token could have been generated during the test
        token = self.env['oauth.provider.token'].search([
            ('client_id', '=', self.client.id),
        ], order='id DESC', limit=1)
        # The response should be a redirect to the redirect URI, with the
        # token added as GET parameter
        self.assertEqual(response.status_code, 302)
        query_string = oauthlib.common.urlencode({
            'access_token': token.token,
            'expires_in': 3600,
            'token_type': token.token_type,
            'scope': token.scope_ids.code,
            'state': state,
        }.items())
        self.assertEqual(
            response.headers['Location'], '{uri_base}#{query_string}'.format(
                uri_base=self.redirect_uri_base, query_string=query_string))
        self.assertEqual(token.user_id, self.user)
