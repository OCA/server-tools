# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import responses
import mock
from openerp import exceptions
from .common import (
    TestKeycloakWizBase, FAKE_USERS_RESPONSE
)


FAKE_NEW_USER = {
    u'username': u'mmouse',
    u'access': {
        u'manage': True,
        u'manageGroupMembership': True,
        u'impersonate': True,
        u'mapRoles': True,
        u'view': True
    },
    u'firstName': u'Micky',
    u'notBefore': 0,
    u'emailVerified': False,
    u'requiredActions': [],
    u'enabled': True,
    u'email': u'mickey@mouse.com',
    u'createdTimestamp': 1539871348883,
    u'totp': False,
    u'disableableCredentialTypes': [],
    u'lastName': u'Mouse',
    u'id': u'1feb89e6-76bd-44a1-ab5d-df28b2477e19',
}


class TestWizard(TestKeycloakWizBase):

    wiz_model = 'auth.keycloak.create.wiz'

    @classmethod
    def setUpClass(cls):
        super(TestWizard, cls).setUpClass()
        cls.user_mickey = cls.env['res.users'].create({
            'name': 'Mickey Mouse',
            'login': 'mmouse',
            'email': 'mickey@mouse.com',
        })

    def test_create_user_values(self):
        values = self.wiz._create_user_values(self.user_donald)
        self.assertDictEqual(values, {
            'username': 'dduck',
            'email': 'donald@duck.com',
            'firstName': 'Donald',
            'lastName': 'Duck',
        })
        values = self.wiz._create_user_values(self.user_john)
        self.assertDictEqual(values, {
            'username': 'jdoe',
            'email': 'john@doe.com',
            'firstName': 'John',
            'lastName': 'Doe',
        })

    @responses.activate
    def test_get_or_create_user_exists(self):
        # make users endpoint return one user less
        responses.add(
            responses.GET,
            self.wiz.endpoint,
            # return only one
            json=FAKE_USERS_RESPONSE[1:2],
            status=200,
            content_type='application/json',
        )
        with mock.patch.object(
            type(self.wiz), '_create_user'
        ) as mock_create_user:
            kk_user = self.wiz._get_or_create_user('TOKEN', self.user_donald)

        self.assertEqual(kk_user['id'], FAKE_USERS_RESPONSE[1]['id'])
        # user exists, no call to create user issued
        self.assertFalse(mock_create_user.called)
        # indeed we find only 1 calls
        self.assertEqual(len(responses.calls), 1)
        request = responses.calls[0].request
        self.assertEqual(
            request.url,
            self.wiz.endpoint + '?search=%s' % self.user_donald.login
        )
        auth = request.headers['Authorization'].replace('Bearer ', '')
        self.assertEqual(auth, 'TOKEN')

    @responses.activate
    def test_get_or_create_user_not_exists(self):
        # mock 1st call to get all users: no users
        responses.add(
            responses.GET,
            self.wiz.endpoint,
            json=[],
            status=200,
            content_type='application/json',
        )
        # mock 2nd call to create a new user: all good, nothing back
        responses.add(
            responses.POST,
            self.wiz.endpoint,
            body='',
            status=200,
            content_type='application/json',
        )
        # mock 3rd call to retrieve new user's data
        # yes, Keycloak sends back NOTHING :(
        responses.add(
            responses.GET,
            self.wiz.endpoint,
            json=[FAKE_NEW_USER, ],
            status=200,
            content_type='application/json',
        )
        kk_user = self.wiz._get_or_create_user('TOKEN', self.user_mickey)
        self.assertDictEqual(kk_user, FAKE_NEW_USER)
        self.assertEqual(len(responses.calls), 3)
        request = responses.calls[0].request
        self.assertEqual(
            request.url,
            self.wiz.endpoint + '?search=%s' % self.user_mickey.login
        )
        auth = request.headers['Authorization'].replace('Bearer ', '')
        self.assertEqual(auth, 'TOKEN')

    @responses.activate
    def test_create_user_conflict(self):
        # simulate again we found no user
        responses.add(
            responses.GET,
            self.wiz.endpoint,
            json=[],
            status=200,
            content_type='application/json',
        )
        # and we try to create a new one, but
        # simulate HTTPError: 409 Client Error:
        # Conflict for url: https://keycloak/auth/admin/realms/Odoo/users
        responses.add(
            responses.POST,
            self.wiz.endpoint,
            body='',
            status=409,
            content_type='application/json',
        )
        with self.assertRaises(exceptions.UserError) as err:
            self.wiz._get_or_create_user('TOKEN', self.user_mickey)
        self.assertEqual(len(responses.calls), 2)
        self.assertTrue(
            err.exception.name.startswith('Conflict on user values.')
        )
