# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import json
import mock
import logging
from datetime import datetime
from openerp import fields

_logger = logging.getLogger(__name__)


class TestOAuthProviderAurhorizeController(object):
    def test_authorize_error_missing_arguments(self):
        """ Call /oauth2/authorize without any argument

        Must return an unknown client identifier error
        """
        self.login('demo', 'demo')
        response = self.get_request('/oauth2/authorize')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Unknown Client Identifier!' in str(response.data))
        self.assertTrue(
            'This client identifier is invalid.' in str(response.data))

    def test_authorize_error_invalid_request(self):
        """ Call /oauth2/authorize with only the client_id argument

        Must return an invalid_request error
        """
        self.login('demo', 'demo')
        response = self.get_request('/oauth2/authorize', data={
            'client_id': self.client.identifier,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Error: invalid_request' in str(response.data))
        self.assertTrue('An unknown error occured! Please contact your '
                        'administrator' in str(response.data))

    def test_authorize_error_unsupported_response_type(self):
        """ Call /oauth2/authorize with an unsupported response type

        Must return an unsupported_response_type error
        """
        self.login('demo', 'demo')
        response = self.get_request('/oauth2/authorize', data={
            'client_id': self.client.identifier,
            'response_type': 'wrong response type',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            'Error: unsupported_response_type' in str(response.data))
        self.assertTrue('An unknown error occured! Please contact your '
                        'administrator' in str(response.data))

    def test_authorize_error_wrong_scopes(self):
        """ Call /oauth2/authorize with wrong scopes

        Must return an invalid_scope error
        """
        self.login('demo', 'demo')
        response = self.get_request('/oauth2/authorize', data={
            'client_id': self.client.identifier,
            'response_type': self.client.response_type,
            'scope': 'wrong scope',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Error: invalid_scope' in str(response.data))
        self.assertTrue('An unknown error occured! Please contact your '
                        'administrator' in str(response.data))

    def test_authorize_error_wrong_uri(self):
        """ Call the authorize method with a wrong redirect_uri

        Must return an invalid_request error
        """
        self.login('demo', 'demo')
        response = self.get_request('/oauth2/authorize', data={
            'client_id': self.client.identifier,
            'response_type': self.client.response_type,
            'redirect_uri': 'http://wrong.redirect.uri',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Error: invalid_request' in str(response.data))
        self.assertTrue('Mismatching redirect URI' in str(response.data))

    def test_authorize_error_missing_uri(self):
        """ Call /oauth2/authorize without any configured redirect URI

        Must return an invalid_request error
        """
        self.client.redirect_uri_ids.unlink()
        self.login('demo', 'demo')
        response = self.get_request('/oauth2/authorize', data={
            'client_id': self.client.identifier,
            'response_type': self.client.response_type,
            'scope': self.client.scope_ids[0].code,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Error: invalid_request' in str(response.data))
        self.assertTrue('Missing redirect URI.' in str(response.data))

    def test_authorize_post_errors(self):
        """ Call /oauth2/authorize in POST without any session

        Must return an unknown client identifier error
        """
        self.login('demo', 'demo')
        response = self.post_request('/oauth2/authorize')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Unknown Client Identifier!' in str(response.data))
        self.assertTrue(
            'This client identifier is invalid.' in str(response.data))

    @mock.patch('openerp.http.WebRequest.env', new_callable=mock.PropertyMock)
    def test_authorize_unsafe_chars(self, request_env):
        """ Call /oauth2/authorize with unsafe chars in the query string """
        # Mock the http request's environ to allow it to see test records
        request_env.return_value = self.env(user=self.user)

        query_string = 'client_id=%s&response_type=%s&state={}' % (
            self.client.identifier,
            self.client.response_type,
        )
        self.login('demo', 'demo')
        response = self.test_client.get(
            '/oauth2/authorize', query_string=query_string,
            environ_base=self.werkzeug_environ)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.name in str(response.data))


class TestOAuthProviderRefreshTokenController(object):
    def test_refresh_token_error_too_much_scopes(self):
        """ Call /oauth2/token using a refresh token, with too much scopes """
        token = self.new_token()
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'scope': self.client.scope_ids.mapped('code'),
            'grant_type': 'refresh_token',
            'refresh_token': token.refresh_token,
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.data), {'error': 'invalid_scope'})

    def test_refresh_token(self):
        """ Get a new token using the refresh token """
        token = self.new_token()
        token.scope_ids = self.client.scope_ids[0]
        response = self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'scope': ' '.join(token.scope_ids.mapped('code')),
            'grant_type': 'refresh_token',
            'refresh_token': token.refresh_token,
        })
        response_data = json.loads(response.data)
        # A new token should have been generated
        # We can safely pick the latest generated token here, because no other
        # token could have been generated during the test
        new_token = self.env['oauth.provider.token'].search([
            ('client_id', '=', self.client.id)
        ], order='id DESC', limit=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_token.token, response_data['access_token'])
        self.assertEqual(new_token.token_type, response_data['token_type'])
        self.assertEqual(
            new_token.refresh_token, response_data['refresh_token'])
        self.assertEqual(new_token.scope_ids, token.scope_ids)
        self.assertEqual(new_token.user_id, self.user)


class TestOAuthProviderTokeninfoController(object):
    def test_tokeninfo_error_missing_arguments(self):
        """ Call /oauth2/tokeninfo without any argument

        Must retun an invalid_or_expired_token error
        """
        response = self.get_request('/oauth2/tokeninfo')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_or_expired_token'})

    def test_tokeninfo(self):
        """ Retrieve token information """
        token = self.new_token()
        token.scope_ids = self.client.scope_ids[0]
        response = self.get_request('/oauth2/tokeninfo', data={
            'access_token': token.token,
        })
        token_lifetime = (fields.Datetime.from_string(
            token.expires_at) - datetime.now()).seconds
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response_data['audience'], token.client_id.identifier)
        self.assertEqual(
            response_data['scopes'], ' '.join(token.scope_ids.mapped('code')))
        # Test a range because the test might not be accurate, depending on the
        # test system load
        self.assertTrue(
            token_lifetime - 5 < response_data['expires_in'] <
            token_lifetime + 5)
        identifier = str(
            token.client_id.identifier + token.user_id.oauth_identifier)
        self.assertEqual(
            response_data['user_id'],
            hashlib.sha256(identifier.encode()).hexdigest())

    def test_tokeninfo_without_scopes(self):
        """ Call /oauth2/tokeninfo without any scope

        Retrieve token information without any scopes on the token
        The user_id field should not be included
        """
        token = self.new_token()
        token.scope_ids = self.env['oauth.provider.scope']
        response = self.get_request('/oauth2/tokeninfo', data={
            'access_token': token.token,
        })
        token_lifetime = (fields.Datetime.from_string(
            token.expires_at) - datetime.now()).seconds
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response_data['audience'], token.client_id.identifier)
        self.assertEqual(
            response_data['scopes'], ' '.join(token.scope_ids.mapped('code')))
        # Test a range because the test might not be accurate, depending on the
        # test system load
        self.assertTrue(
            token_lifetime - 5 < response_data['expires_in'] <
            token_lifetime + 5)


class TestOAuthProviderUserinfoController(object):
    def test_userinfo_error_missing_arguments(self):
        """ Call /oauth2/userinfo without any argument

        Must return an invalid_or_expired_token error
        """
        response = self.get_request('/oauth2/userinfo')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_or_expired_token'})

    def test_userinfo_single_scope(self):
        """ Retrieve user information with only a single scope """
        token = self.new_token()
        token.scope_ids = self.client.scope_ids[0]

        # Retrieve user information
        response = self.get_request('/oauth2/userinfo', data={
            'access_token': token.token,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {
            'id': self.user.id,
            'email': self.user.email,
        })

    def test_userinfo_multiple_scope(self):
        """ Retrieve user information with only a all test scopes """
        token = self.new_token()
        token.scope_ids = self.client.scope_ids

        # Retrieve user information
        response = self.get_request('/oauth2/userinfo', data={
            'access_token': token.token,
        })
        # The Email scope allows to read the email
        # The Profile scope allows to read the name and city
        # The id of the recod is always added (standard Odoo behaviour)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {
            'id': self.user.id,
            'name': self.user.name,
            'email': self.user.email,
            'city': self.user.city,
        })


class TestOAuthProviderOtherinfoController(object):
    def test_otherinfo_error_missing_arguments(self):
        """ Call /oauth2/otherinfo method without any argument

        Must return an invalid_or_expired_token error
        """
        response = self.get_request('/oauth2/otherinfo')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_or_expired_token'})

    def test_otherinfo_error_missing_model(self):
        """ Call /oauth2/otherinfo method without the model argument

        Must return an invalid_model error
        """
        token = self.new_token()
        response = self.get_request(
            '/oauth2/otherinfo', data={'access_token': token.token})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {'error': 'invalid_model'})

    def test_otherinfo_error_invalid_model(self):
        """ Call /oauth2/otherinfo method with an invalid model

        Must return an invalid_model error
        """
        token = self.new_token()
        response = self.get_request(
            '/oauth2/otherinfo',
            data={'access_token': token.token, 'model': 'invalid.model'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {'error': 'invalid_model'})

    def test_otherinfo_user_information(self):
        """ Call /oauth2/otherinfo to retrieve information using the token """
        token = self.new_token()
        token.scope_ids = self.client.scope_ids

        # Add a new scope to test informations retrieval
        token.scope_ids += self.env['oauth.provider.scope'].create({
            'name': 'Groups',
            'code': 'groups',
            'description': 'List of accessible groups',
            'model_id': self.env.ref('base.model_res_groups').id,
            'filter_id': False,
            'field_ids': [
                (6, 0, [self.env.ref('base.field_res_groups_name').id]),
            ],
        })
        # Retrieve user information
        response = self.get_request('/oauth2/otherinfo', data={
            'access_token': token.token,
            'model': 'res.users',
        })
        # The Email scope allows to read the email
        # The Profile scope allows to read the name and city
        # The id of the recod is always added (standard Odoo behaviour)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {str(self.user.id): {
            'id': self.user.id,
            'name': self.user.name,
            'email': self.user.email,
            'city': self.user.city,
        }})

    def test_otherinfo_group_information(self):
        """ Call /oauth2/otherinfo to retrieve information using the token """
        token = self.new_token()
        token.scope_ids = self.client.scope_ids

        # Add a new scope to test informations retrieval
        token.scope_ids += self.env['oauth.provider.scope'].create({
            'name': 'Groups',
            'code': 'groups',
            'description': 'List of accessible groups',
            'model_id': self.env.ref('base.model_res_groups').id,
            'filter_id': False,
            'field_ids': [
                (6, 0, [self.env.ref('base.field_res_groups_name').id]),
            ],
        })

        # Retrieve groups information
        all_groups = self.env['res.groups'].search([])
        response = self.get_request('/oauth2/otherinfo', data={
            'access_token': token.token,
            'model': 'res.groups',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(json.loads(response.data).keys()),
            sorted(map(str, all_groups.ids)))


class TestOAuthProviderRevokeTokenController(object):
    def test_revoke_token_error_missing_arguments(self):
        """ Call /oauth2/revoke_token method without any argument """
        response = self.post_request('/oauth2/revoke_token')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_or_expired_token'})

    def test_revoke_token_error_missing_client_id(self):
        """ Call /oauth2/revoke_token method without client identifier """
        token = self.new_token()
        response = self.post_request('/oauth2/revoke_token', data={
            'token': token.token,
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_client'})

    def test_revoke_token_error_missing_token(self):
        """ Call /oauth2/revoke_token method without token """
        response = self.post_request('/oauth2/revoke_token', data={
            'client_id': self.client.identifier,
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data), {'error': 'invalid_or_expired_token'})

    def test_revoke_access_token(self):
        """ Revoke an access token """
        token = self.new_token()
        self.post_request('/oauth2/revoke_token', data={
            'client_id': self.client.identifier,
            'token': token.token,
        })
        self.assertFalse(token.exists())

    def test_revoke_refresh_token(self):
        """ Revoke a refresh token """
        token = self.new_token()
        self.post_request('/oauth2/revoke_token', data={
            'client_id': self.client.identifier,
            'token': token.refresh_token,
        })
        self.assertTrue(token.exists())
        self.assertFalse(token.refresh_token)
