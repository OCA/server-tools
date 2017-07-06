# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo.tests.common import TransactionCase
from ..oauth2.validator import OdooValidator

_logger = logging.getLogger(__name__)

try:
    from oauthlib import oauth2
except ImportError:
    _logger.debug('Cannot `import oauthlib`.')


class TestOAuthProviderClient(TransactionCase):

    def setUp(self):
        super(TestOAuthProviderClient, self).setUp()
        self.client_vals = {
            'name': 'Client',
            'identifier': 'client',
        }

    def new_client(self, vals=None):
        values = self.client_vals.copy()
        if vals is not None:
            values.update(vals)

        return self.env['oauth.provider.client'].create(values)

    def test_grant_response_type_default(self):
        """ Check the value of the grant_type and response_type fields """
        # Default : Web Application
        client = self.new_client({'identifier': 'default'})
        self.assertEqual(client.grant_type, 'authorization_code')
        self.assertEqual(client.response_type, 'code')

    def test_grant_response_type_web_application(self):
        """ Check the value of the grant_type and response_type fields """
        # Web Application
        client = self.new_client(vals={'application_type': 'web application'})
        self.assertEqual(client.grant_type, 'authorization_code')
        self.assertEqual(client.response_type, 'code')

    def test_grant_response_type_mobile_application(self):
        """ Check the value of the grant_type and response_type fields """
        # Mobile Application
        client = self.new_client(
            vals={'application_type': 'mobile application'})
        self.assertEqual(client.grant_type, 'implicit')
        self.assertEqual(client.response_type, 'token')

    def test_grant_response_type_legacy_application(self):
        """ Check the value of the grant_type and response_type fields """
        # Legacy Application
        client = self.new_client(
            vals={'application_type': 'legacy application'})
        self.assertEqual(client.grant_type, 'password')
        self.assertEqual(client.response_type, 'none')

    def test_grant_response_type_backend_application(self):
        """ Check the value of the grant_type and response_type fields """
        # Backend Application
        client = self.new_client(
            vals={'application_type': 'backend application'})
        self.assertEqual(client.grant_type, 'client_credentials')
        self.assertEqual(client.response_type, 'none')

    def test_get_oauth2_server_default(self):
        """ Check the returned server, depending on the application type """
        # Default : Web Application
        client = self.new_client({'identifier': 'default'})
        self.assertTrue(
            isinstance(client.get_oauth2_server(),
                       oauth2.WebApplicationServer))

    def test_get_oauth2_server_web_application(self):
        """ Check the returned server, depending on the application type """
        # Web Application
        client = self.new_client(vals={'application_type': 'web application'})
        self.assertTrue(
            isinstance(client.get_oauth2_server(),
                       oauth2.WebApplicationServer))

    def test_get_oauth2_server_mobile_application(self):
        """ Check the returned server, depending on the application type """
        # Mobile Application
        client = self.new_client(
            vals={'application_type': 'mobile application'})
        self.assertTrue(
            isinstance(client.get_oauth2_server(),
                       oauth2.MobileApplicationServer))

    def test_get_oauth2_server_legacy_applicaton(self):
        """ Check the returned server, depending on the application type """
        # Legacy Application
        client = self.new_client(
            vals={'application_type': 'legacy application'})
        self.assertTrue(
            isinstance(client.get_oauth2_server(),
                       oauth2.LegacyApplicationServer))

    def test_get_oauth2_server_backend_application(self):
        """ Check the returned server, depending on the application type """
        # Backend Application
        client = self.new_client(
            vals={'application_type': 'backend application'})
        self.assertTrue(
            isinstance(client.get_oauth2_server(),
                       oauth2.BackendApplicationServer))

    def test_get_oauth2_server_validator(self):
        """ Check the validator of the returned server """
        client = self.new_client()
        # No defined validator: Check that an OdooValidator instance is created
        self.assertTrue(
            isinstance(client.get_oauth2_server().request_validator,
                       OdooValidator))

    def test_get_oauth2_server_validator_custom(self):
        """ Check the validator of the returned server """
        client = self.new_client()
        # Passed validator : Check that the validator instance is used
        validator = OdooValidator()
        self.assertEqual(
            client.get_oauth2_server(validator).request_validator, validator)
