# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import responses
import base64
import urlparse
from .common import (
    TestKeycloakWizBase, FAKE_TOKEN_RESPONSE, FAKE_USERS_RESPONSE
)


class TestWizard(TestKeycloakWizBase):

    wiz_model = 'auth.keycloak.sync.wiz'

    def setUp(self):
        super(TestWizard, self).setUp()
        responses.add(
            responses.GET,
            self.wiz.endpoint,
            json=FAKE_USERS_RESPONSE,
            status=200,
            content_type='application/json',
        )

    @responses.activate
    def test_get_token(self):
        token = self.wiz._get_token()
        self.assertEqual(len(responses.calls), 1)
        self.assertDictEqual(
            responses.calls[0].response.json(), FAKE_TOKEN_RESPONSE
        )
        self.assertEqual(token, FAKE_TOKEN_RESPONSE['access_token'])
        request = responses.calls[0].request
        self.assertEqual(request.url, self.provider.auth_endpoint)
        expected = [
            ('username', 'admin'),
            ('client_secret', 'c35a795e-65ef-432d-97fb-6ef4bea84bb8'),
            ('password', 'well, yes, is "admin"'),
            ('client_id', 'odoo'),
            ('grant_type', 'password')
        ]
        self.assertListEqual(urlparse.parse_qsl(request.body), expected)

    @responses.activate
    def test_get_users(self):
        token = self.wiz._get_token()
        users = self.wiz._get_users(token)
        self.assertEqual(len(responses.calls), 2)
        self.assertListEqual(
            responses.calls[1].response.json(), FAKE_USERS_RESPONSE
        )
        self.assertEqual(len(users), 2)
        request = responses.calls[1].request
        self.assertEqual(request.url, self.wiz.endpoint)
        auth = request.headers['Authorization'].replace('Bearer ', '')
        self.assertEqual(base64.decodestring(auth), 'my nice token')

    @responses.activate
    def test_sync_by_username(self):
        self.assertFalse(self.user_donald.oauth_uid)
        self.assertFalse(self.user_john.oauth_uid)
        self.assertEqual(self.wiz.login_match_key, 'username:login')
        action = self.wiz.button_sync()
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(
            action['domain'], [
                ('id', 'in', (self.user_donald + self.user_john).ids)
            ]
        )
        self.assertEqual(
            self.user_donald.oauth_uid,
            u'1feb89e6-76bd-44a1-ab5d-df28b6477e19'
        )
        self.assertEqual(
            self.user_donald.oauth_provider_id, self.provider
        )
        self.assertEqual(
            self.user_john.oauth_uid,
            u'ef1d2e5d-1aad-4daf-858e-f246168a10ef'
        )
        self.assertEqual(
            self.user_john.oauth_provider_id, self.provider
        )

    @responses.activate
    def test_sync_by_email(self):
        self.assertFalse(self.user_donald.oauth_uid)
        self.assertFalse(self.user_john.oauth_uid)
        self.wiz.login_match_key = 'email:partner_id.email'
        action = self.wiz.button_sync()
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(
            action['domain'], [
                ('id', 'in', (self.user_donald + self.user_john).ids)
            ]
        )
        self.assertEqual(
            self.user_donald.oauth_uid,
            u'1feb89e6-76bd-44a1-ab5d-df28b6477e19'
        )
        self.assertEqual(
            self.user_donald.oauth_provider_id, self.provider
        )
        self.assertEqual(
            self.user_john.oauth_uid,
            u'ef1d2e5d-1aad-4daf-858e-f246168a10ef'
        )
        self.assertEqual(
            self.user_john.oauth_provider_id, self.provider
        )
