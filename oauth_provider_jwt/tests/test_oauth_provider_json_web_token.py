# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import exceptions
from openerp.addons.oauth_provider.tests.common_test_controller import \
    OAuthProviderControllerTransactionCase
from ..models.oauth_provider_client import OAuthProviderClient

_logger = logging.getLogger(__name__)

try:
    import jwt
except ImportError:
    _logger.debug('Cannot `import jwt`.')


class TestOAuthProviderController(OAuthProviderControllerTransactionCase):
    def setUp(self):
        # Use the legacy appication profile for tests to execute all requests
        # as public user. This allows to rightly tests access rghts
        super(TestOAuthProviderController, self).setUp('legacy application')

        # Configure the client to generate a JSON Web Token
        self.client.token_type = 'jwt'

        # Define base values for a scope creation
        self.filter = self.env['ir.filters'].create({
            'name': 'User filter',
            'model_id': 'res.users',
            'domain': "[('id', '=', uid)]",
        })
        self.scope_vals = {
            'name': 'Scope',
            'code': 'scope',
            'description': 'Description of the scope',
            'model_id': self.env.ref('base.model_res_users').id,
            'filter_id': self.filter.id,
            'field_ids': [
                (6, 0, [self.env.ref('base.field_res_users_email').id]),
            ],
        }

    def new_scope(self):
        return self.env['oauth.provider.scope'].create(self.scope_vals)

    def generate_private_key(self):
        """ Generates a private key depending on the algorithm

        Returns the key needed to decode the signature
        """
        if self.client.jwt_algorithm[:2] not in \
           OAuthProviderClient.CRYPTOSYSTEMS:
            # Use the private key as decoding key for symetric algorithms
            self.client.jwt_private_key = 'secret key'
            decoding_key = self.client.jwt_private_key
        else:
            # Generate a random private key for asymetric algorithms
            self.client.generate_private_key()
            decoding_key = self.client.jwt_public_key

        return decoding_key

    def common_test_json_web_token(self, algorithm):
        """ Check generation of a JSON Web Token using a symetric algorithm """
        # Configure the client to use an HS512 algorithm
        self.client.jwt_algorithm = algorithm
        decoding_key = self.generate_private_key()

        # Ask a token to the server
        state = 'Some custom state'
        self.post_request('/oauth2/token', data={
            'client_id': self.client.identifier,
            'scope': self.client.scope_ids[0].code,
            'grant_type': self.client.grant_type,
            'username': self.user.login,
            'password': 'demo',
            'state': state,
        })
        # A new token should have been generated
        # We can safely pick the latest generated token here, because no other
        # token could have been generated during the test
        token = self.env['oauth.provider.token'].search([
            ('client_id', '=', self.client.id),
        ], order='id DESC', limit=1)

        # Check token's contents
        token_contents = jwt.decode(
            token.token,
            decoding_key,
            algorithm=self.client.jwt_algorithm,
            audience=self.client.identifier,
        )
        self.assertEqual(token_contents['user_id'], token.generate_user_id())
        return token_contents

    def test_json_web_token_hs256(self):
        """ Execute the JSON Web Token test using HS256 algorithm """
        token_contents = self.common_test_json_web_token('HS256')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_hs384(self):
        """ Execute the JSON Web Token test using HS384 algorithm """
        token_contents = self.common_test_json_web_token('HS384')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_hs512(self):
        """ Execute the JSON Web Token test using HS512 algorithm """
        token_contents = self.common_test_json_web_token('HS512')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_es256(self):
        """ Execute the JSON Web Token test using ES256 algorithm """
        token_contents = self.common_test_json_web_token('ES256')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_es384(self):
        """ Execute the JSON Web Token test using ES384 algorithm """
        token_contents = self.common_test_json_web_token('ES384')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_es512(self):
        """ Execute the JSON Web Token test using ES512 algorithm """
        token_contents = self.common_test_json_web_token('ES512')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_rs256(self):
        """ Execute the JSON Web Token test using RS256 algorithm """
        token_contents = self.common_test_json_web_token('RS256')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_rs384(self):
        """ Execute the JSON Web Token test using RS384 algorithm """
        token_contents = self.common_test_json_web_token('RS384')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_rs512(self):
        """ Execute the JSON Web Token test using RS512 algorithm """
        token_contents = self.common_test_json_web_token('RS512')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_ps256(self):
        """ Execute the JSON Web Token test using PS256 algorithm """
        token_contents = self.common_test_json_web_token('PS256')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_ps384(self):
        """ Execute the JSON Web Token test using PS384 algorithm """
        token_contents = self.common_test_json_web_token('PS384')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_ps512(self):
        """ Execute the JSON Web Token test using PS512 algorithm """
        token_contents = self.common_test_json_web_token('PS512')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id']))

    def test_json_web_token_with_scope(self):
        """ Execute the JSON Web Token test with additional scope data """
        self.client.jwt_scope_id = self.new_scope()
        token_contents = self.common_test_json_web_token('PS512')
        self.assertEqual(
            sorted(token_contents.keys()),
            sorted(['exp', 'nbf', 'iss', 'aud', 'iat', 'user_id', 'email']))
        self.assertEqual(token_contents['email'], self.user.email)

    def test_empty_public_key_for_symetric_algorithm(self):
        """ Check that symetric algorithm return an empty public key """
        self.client.jwt_algorithm = 'HS512'
        self.client.jwt_private_key = 'secret key'
        self.assertEqual(self.client.jwt_public_key, False)

    def test_generate_private_key_for_symetric_algorithm(self):
        """ Check that symetric algorithm don't generate random private key """
        self.client.jwt_algorithm = 'HS512'
        with self.assertRaises(exceptions.UserError):
            self.client.generate_private_key()

    def test_private_key_constraint(self):
        """ Check the private key/algorithm consistency constraint """
        self.client.jwt_algorithm = 'ES512'
        # Generate an ECDSA private key
        self.client.generate_private_key()

        with self.assertRaises(exceptions.ValidationError):
            # Check that the ECDSA private key is not allowed for an RSA
            # configured client
            self.client.jwt_algorithm = 'RS512'

    def test_public_key_retrieval_without_argument(self):
        """ Check the /oauth2/public_key route """
        response = self.get_request('/oauth2/public_key')
        self.assertEqual(response.data, '')

    def test_public_key_retrieval_symetric(self):
        """ Check the /oauth2/public_key route """
        self.client.jwt_algorithm = 'HS512'
        self.generate_private_key()
        response = self.get_request('/oauth2/public_key', data={
            'client_id': self.client.identifier,
        })
        self.assertEqual(response.data, '')

    def test_public_key_retrieval_asymetric(self):
        """ Check the /oauth2/public_key route """
        self.client.jwt_algorithm = 'RS512'
        public_key = self.generate_private_key()
        response = self.get_request('/oauth2/public_key', data={
            'client_id': self.client.identifier,
        })
        self.assertEqual(response.data, public_key)
