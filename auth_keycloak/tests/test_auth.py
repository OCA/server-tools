# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import responses

from .common import TestKeycloakBase
from ..exceptions import OAuthError


VALIDATE_RESP_BODY = {
    "jti": "36acb399-31ed-4b0b-8f2e-4f645ab6d8c7",
    "exp": 1525419762,
    "nbf": 0,
    "iat": 1525419462,
    "iss": "https://keycloak/auth/realms/Odoo",
    "aud": "odoo",
    "sub": "df5ab747-2b80-4c18-bd03-5f3d3b2c0fd6",
    "typ": "Bearer",
    "azp": "odoo",
    "auth_time": 0,
    "session_state": "a82adc36-18ad-4a39-874d-abe9747205ba",
    "name": "CampToCamp -",
    "given_name": "CampToCamp",
    "family_name": "-",
    "preferred_username": "c2c",
    "email": "foo@camptocamp.com",
    "acr": "1",
    "allowed-origins": [
        "*"
    ],
    "realm_access": {
        "roles": [
            "uma_authorization"
        ]
    },
    "resource_access": {
        "my-company": {
            "roles": [
                "user"
            ]
        },
        "odoo": {
            "roles": [
                "user"
            ]
        },
        "api-gateway": {
            "roles": [
                "user"
            ]
        },
        "user-service": {
            "roles": [
                "reader"
            ]
        },
        "account": {
            "roles": [
                "manage-account",
                "manage-account-links",
                "view-profile"
            ]
        }
    },
    "client_id": "odoo",
    "username": "c2c",
    "active": True
}


class TestAuth(TestKeycloakBase):

    @responses.activate
    def test_validate_auth(self):
        """Validate request has basic auth header."""
        responses.add(
            responses.POST,
            self.provider.validation_endpoint,
            json=VALIDATE_RESP_BODY,
            status=200,
            content_type='application/json',
        )
        access_token = 'XXXXXXX'
        self.env['res.users']._auth_oauth_validate(
            self.provider.id, access_token)
        self.assertEqual(len(responses.calls), 1)
        request = responses.calls[0].request
        self._assert_request_auth_header(request)

    @responses.activate
    def test_validate(self):
        responses.add(
            responses.POST,
            self.provider.validation_endpoint,
            json=VALIDATE_RESP_BODY,
            status=200,
            content_type='application/json',
        )
        access_token = 'XXXXXXX'
        result = self.env['res.users']._auth_oauth_validate(
            self.provider.id, access_token)
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            result['sub'], 'df5ab747-2b80-4c18-bd03-5f3d3b2c0fd6'
        )
        self.assertEqual(
            result['user_id'], 'df5ab747-2b80-4c18-bd03-5f3d3b2c0fd6'
        )

    @responses.activate
    def test_validate_error(self):
        responses.add(
            responses.POST,
            self.provider.validation_endpoint,
            json={"error": "Something bad happened"},
            status=200,
            content_type='application/json',
        )
        access_token = 'XXXXXXX'
        with self.assertRaises(OAuthError):
            self.env['res.users']._auth_oauth_validate(
                self.provider.id, access_token)
        self.assertEqual(len(responses.calls), 1)
