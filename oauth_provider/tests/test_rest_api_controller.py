# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json

from .common_test_controller import OauthProviderControllerTransactionCase


class TestRestApiController(OauthProviderControllerTransactionCase):

    API_BASE = '/api/rest/1.0/res.users'

    def setUp(self):
        super(TestRestApiController, self).setUp('legacy application')
        self.logged_user = self.env.user
        self.user = self.env.user
        self.token = self.new_token(True).token
        self.filter.domain = []
        self.admin_user_data = {"city": self.user.city,
                                "login": self.user.login,
                                "id": self.user.id,
                                "name": self.user.name,
                                "email": self.user.email}

    def _test_json_response(self, response, expect, res_id=None):
        # Python does some funny things on the object encode.
        # Must encode/decode the expect object to get compatible data.
        expect = json.loads(json.dumps(expect))
        response = json.loads(response.data)
        expect = {
            u"jsonrpc": u"2.0",
            u"id": res_id,
            u"result": expect,
        }
        self.assertDictEqual(response, expect)

    def test_rest_list_all(self):
        """ It should return all of the scoped data. """
        self.filter.domain = [('id', '=', self.env.uid)]
        data = {'access_token': self.token}
        response = self.get_request(self.API_BASE, data=data, json=True)
        self._test_json_response(response, {self.uid: self.admin_user_data})

    def test_rest_list_domain(self):
        """ It should only return scoped data indicated by the query. """
        data = {
            'access_token': self.token,
            'domain': [("name", "=", self.admin_user_data['name'])],
        }
        response = self.get_request(self.API_BASE, data=data, json=True)
        self._test_json_response(response, {self.uid: self.admin_user_data})

    def test_rest_read(self):
        """ It should return the proper record. """
        response = self.get_request(
            '%s/%s' % (self.API_BASE, self.env.uid),
            data={'access_token': self.token,
                  'domain': [('name', '=', self.admin_user_data['name'])],
                  },
            json=True,
        )
        self._test_json_response(response, self.admin_user_data)

    def test_rest_create(self):
        """ It should create and return a new record. """
        response = self.post_request(
            self.API_BASE,
            data={'access_token': self.token,
                  'name': 'Test User',
                  'login': 'tuser@example.com',
                  },
            json=True,
        )
        expect = {"city": False,
                  "login": "tuser@example.com",
                  "id": json.loads(response.data)['result']['id'],
                  "name": "Test User",
                  "email": False}
        self._test_json_response(response, expect)

    def test_rest_write(self):
        """ It should write to and return the updated record data. """
        response = self.put_request(
            '%s/%s' % (self.API_BASE, self.env.uid),
            data={'access_token': self.token,
                  'name': 'Edited User',
                  },
            json=True,
        )
        self.admin_user_data['name'] = 'Edited User'
        self._test_json_response(response, self.admin_user_data)

    def test_rest_delete(self):
        """ It should delete the record and return True """
        user = self.env.ref('base.user_demo')
        response = self.delete_request(
            '%s/%s' % (self.API_BASE, user.id),
            data={'access_token': self.token},
            json=True,
        )
        self._test_json_response(response, True)

    def test_rest_create_token_validate(self):
        """ It should raise on invalid token. """
        response = self.post_request(
            self.API_BASE,
            data={'access_token': 'Bad Token'},
            json=True,
        )
        response = json.loads(response.data)
        self.assertEqual(response.get('error', {}).get('code'), 401)

    def test_rest_create_bad_scope_field(self):
        """ It should raise on field mutation not within scope. """
        response = self.post_request(
            self.API_BASE,
            data={'access_token': self.token,
                  'signatunre': 'Some non-allowed data',
                  },
            json=True,
        )
        response = json.loads(response.data)
        self.assertEqual(response.get('error', {}).get('code'), 403)

    def test_rest_update_token_validate(self):
        """ It should raise on invalid token. """
        response = self.put_request(
            '%s/%s' % (self.API_BASE, self.env.uid),
            data={'access_token': 'Bad Token'},
            json=True,
        )
        response = json.loads(response.data)
        self.assertEqual(response.get('error', {}).get('code'), 401)

    def test_rest_update_bad_scope_field(self):
        """ It should raise on field mutation not within scope. """
        response = self.put_request(
            '%s/%s' % (self.API_BASE, self.env.uid),
            data={'access_token': self.token,
                  'signatunre': 'Some non-allowed data',
                  },
            json=True,
        )
        response = json.loads(response.data)
        self.assertEqual(response.get('error', {}).get('code'), 403)

    def test_rest_update_bad_scope_record(self):
        """ It should raise on record not within scope. """
        self.filter.domain = [('id', '=', self.env.ref('base.user_demo').id)]
        response = self.put_request(
            '%s/%s' % (self.API_BASE, self.env.uid),
            data={'access_token': self.token,
                  'name': 'Test User',
                  },
            json=True,
        )
        response = json.loads(response.data)
        self.assertEqual(response.get('error', {}).get('code'), 403)

    def test_rest_delete_token_validate(self):
        """ It should raise on invalid token. """
        response = self.delete_request(
            '%s/%s' % (self.API_BASE, self.env.uid),
            data={'access_token': 'Bad Token'},
            json=True,
        )
        response = json.loads(response.data)
        self.assertEqual(response.get('error', {}).get('code'), 401)

    def test_rest_delete_bad_scope_record(self):
        """ It should raise on record not within scope. """
        self.filter.domain = [('id', '=', self.env.ref('base.user_demo').id)]
        response = self.delete_request(
            '%s/%s' % (self.API_BASE, self.env.uid),
            data={'access_token': self.token},
            json=True,
        )
        response = json.loads(response.data)
        self.assertEqual(response.get('error', {}).get('code'), 403)

    def test_rest_list_token_validate(self):
        """ It should raise on invalid token. """
        response = self.get_request(
            self.API_BASE,
            data={'access_token': 'Bad Token'},
            json=True,
        )
        response = json.loads(response.data)
        self.assertEqual(response.get('error', {}).get('code'), 401)

    def test_rest_read_token_validate(self):
        """ It should raise on invalid token. """
        response = self.get_request(
            '%s/%s' % (self.API_BASE, self.env.uid),
            data={'access_token': 'Bad Token'},
            json=True,
        )
        response = json.loads(response.data)
        self.assertEqual(response.get('error', {}).get('code'), 401)
