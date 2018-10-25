# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import responses
import base64
import odoo.tests.common as common


class TestKeycloakBase(common.SavepointCase):

    base_auth_url = 'https://keycloak/auth'
    base_openid_url = base_auth_url + '/realms/Odoo/protocol/openid-connect'

    @classmethod
    def setUpClass(cls):
        super(TestKeycloakBase, cls).setUpClass()
        cls.env = cls.env(context=dict(
            cls.env.context,
            tracking_disable=True,
            no_reset_password=True
        ))
        cls.provider = cls.env['auth.oauth.provider'].create({
            'name': 'Keycloak',
            'client_id': 'odoo',
            'client_secret': 'c35a795e-65ef-432d-97fb-6ef4bea84bb8',
            'auth_endpoint': cls.base_openid_url + '/token',
            'validation_endpoint':
                cls.base_openid_url + '/token/introspect',
            'body': 'foo',
            'enabled': True,
        })

    def _assert_request_auth_header(self, request):
        """Validate request has basic auth header."""
        auth = request.headers['Authorization'].replace('Basic ', '')
        self.assertEqual(
            base64.decodestring(auth),
            '{}:{}'.format(self.provider.client_id,
                           self.provider.client_secret)
        )


FAKE_TOKEN_RESPONSE = {
    u'session_state': u'623c9060-fd20-40e1-ad31-090bd77d521e',
    u'not-before-policy': 0,
    u'expires_in': 60,
    u'token_type': u'bearer',
    u'refresh_expires_in': 1800,
    u'scope': u'profile email',
    u'access_token': base64.b64encode(u'my nice token'),
    u'refresh_token': base64.b64encode(u'my nice refresh token'),
}
FAKE_USERS_RESPONSE = [{
    u'username': u'jdoe',
    u'access': {
        u'manage': True,
        u'manageGroupMembership': True,
        u'impersonate': True,
        u'mapRoles': True,
        u'view': True
    },
    u'notBefore': 0,
    u'email': u'john@doe.com',
    u'emailVerified': False,
    u'enabled': True,
    u'createdTimestamp': 1539857662328,
    u'totp': False,
    u'disableableCredentialTypes': [u'password'],
    u'requiredActions': [],
    u'id': u'ef1d2e5d-1aad-4daf-858e-f246168a10ef'
}, {
    u'username': u'dduck',
    u'access': {
        u'manage': True,
        u'manageGroupMembership': True,
        u'impersonate': True,
        u'mapRoles': True,
        u'view': True
    },
    u'firstName': u'Donald',
    u'notBefore': 0,
    u'emailVerified': False,
    u'requiredActions': [],
    u'enabled': True,
    u'email': u'donald@duck.com',
    u'createdTimestamp': 1539871348882,
    u'totp': False,
    u'disableableCredentialTypes': [],
    u'lastName': u'Donald',
    u'id': u'1feb89e6-76bd-44a1-ab5d-df28b6477e19',
}]


class TestKeycloakWizBase(TestKeycloakBase):

    wiz_model = ''

    @classmethod
    def setUpClass(cls):
        super(TestKeycloakWizBase, cls).setUpClass()
        cls.users_endpoint = cls.base_auth_url + '/admin/realms/Odoo/users'
        cls.provider.update({
            'users_endpoint': cls.users_endpoint,
            'superuser': 'admin',
            'superuser_pwd': 'well, yes, is "admin"',
        })
        cls.wiz = cls.env[cls.wiz_model].create({
            'provider_id': cls.provider.id,
        })
        # create users matching keycloak response
        cls.user_john = cls.env['res.users'].create({
            'name': 'John Doe',
            'login': 'jdoe',
            'email': 'john@doe.com',
        })
        cls.user_donald = cls.env['res.users'].create({
            'name': 'Donald Duck',
            'login': 'dduck',
            'email': 'donald@duck.com',
        })

    def setUp(self):
        super(TestKeycloakWizBase, self).setUp()
        responses.add(
            responses.POST,
            self.provider.auth_endpoint,
            json=FAKE_TOKEN_RESPONSE,
            status=200,
            content_type='application/json',
        )
