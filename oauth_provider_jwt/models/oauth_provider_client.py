# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, timedelta
from odoo import models, api, fields, exceptions, _

_logger = logging.getLogger(__name__)

try:
    from oauthlib.oauth2.rfc6749.tokens import random_token_generator
except ImportError:
    _logger.debug('Cannot `import oauthlib`.')

try:
    import jwt
except ImportError:
    _logger.debug('Cannot `import jwt`.')

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric.ec import \
        EllipticCurvePrivateKey
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    from cryptography.hazmat.primitives.serialization import \
        Encoding, PublicFormat, PrivateFormat, NoEncryption, \
        load_pem_private_key
    from cryptography.hazmat.primitives.asymmetric import rsa, ec
except ImportError:
    _logger.debug('Cannot `import cryptography`.')


class OAuthProviderClient(models.Model):
    _inherit = 'oauth.provider.client'

    CRYPTOSYSTEMS = {
        'ES': EllipticCurvePrivateKey,
        'RS': RSAPrivateKey,
        'PS': RSAPrivateKey,
    }

    token_type = fields.Selection(selection_add=[('jwt', 'JSON Web Token')])
    jwt_scope_id = fields.Many2one(
        comodel_name='oauth.provider.scope', string='Data Scope',
        domain=[('model_id.model', '=', 'res.users')],
        help='Scope executed to add some user\'s data in the token.')
    jwt_algorithm = fields.Selection(selection=[
        ('HS256', 'HMAC using SHA-256 hash algorithm'),
        ('HS384', 'HMAC using SHA-384 hash algorithm'),
        ('HS512', 'HMAC using SHA-512 hash algorithm'),
        ('ES256', 'ECDSA signature algorithm using SHA-256 hash algorithm'),
        ('ES384', 'ECDSA signature algorithm using SHA-384 hash algorithm'),
        ('ES512', 'ECDSA signature algorithm using SHA-512 hash algorithm'),
        ('RS256', 'RSASSA-PKCS1-v1_5 signature algorithm using SHA-256 hash '
         'algorithm'),
        ('RS384', 'RSASSA-PKCS1-v1_5 signature algorithm using SHA-384 hash '
         'algorithm'),
        ('RS512', 'RSASSA-PKCS1-v1_5 signature algorithm using SHA-512 hash '
         'algorithm'),
        ('PS256', 'RSASSA-PSS signature using SHA-256 and MGF1 padding with '
         'SHA-256'),
        ('PS384', 'RSASSA-PSS signature using SHA-384 and MGF1 padding with '
         'SHA-384'),
        ('PS512', 'RSASSA-PSS signature using SHA-512 and MGF1 padding with '
         'SHA-512'),
    ], string='Algorithm', help='Algorithm used to sign the JSON Web Token.')
    jwt_private_key = fields.Text(
        string='Private Key',
        help='Private key used for the JSON Web Token generation.')
    jwt_public_key = fields.Text(
        string='Public Key', compute='_compute_jwt_public_key',
        help='Public key used for the JSON Web Token generation.')

    @api.multi
    def _load_private_key(self):
        """ Load the client's private key into a cryptography's object instance
        """
        return load_pem_private_key(
            str(self.jwt_private_key),
            password=None,
            backend=default_backend(),
        )

    @api.multi
    @api.constrains('jwt_algorithm', 'jwt_private_key')
    def _check_jwt_private_key(self):
        """ Check if the private key's type matches the selected algorithm

        This check is only performed for asymetric algorithms
        """
        for client in self:
            algorithm_prefix = client.jwt_algorithm[:2]
            if client.jwt_private_key and \
               algorithm_prefix in self.CRYPTOSYSTEMS:
                private_key = client._load_private_key()

                if not isinstance(
                   private_key, self.CRYPTOSYSTEMS[algorithm_prefix]):
                    raise exceptions.ValidationError(
                        _('The private key doesn\'t fit the selected '
                          'algorithm!'))

    @api.multi
    def generate_private_key(self):
        """ Generate a private key for ECDSA and RSA algorithm clients """
        for client in self:
            algorithm_prefix = client.jwt_algorithm[:2]

            if algorithm_prefix == 'ES':
                key = ec.generate_private_key(
                    curve=ec.SECT283R1,
                    backend=default_backend(),
                )
            elif algorithm_prefix in ('RS', 'PS'):
                key = rsa.generate_private_key(
                    public_exponent=65537, key_size=2048,
                    backend=default_backend(),
                )
            else:
                raise exceptions.UserError(
                    _('You can only generate private keys for asymetric '
                      'algorithms!'))

            client.jwt_private_key = key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=NoEncryption(),
            )

    @api.multi
    def _compute_jwt_public_key(self):
        """ Compute the public key associated to the client's private key

        This is only done for asymetric algorithms
        """
        for client in self:
            if client.jwt_private_key and \
               client.jwt_algorithm[:2] in self.CRYPTOSYSTEMS:
                private_key = client._load_private_key()
                client.jwt_public_key = private_key.public_key().public_bytes(
                    Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
            else:
                client.jwt_public_key = False

    @api.model
    def _generate_jwt_payload(self, request):
        """ Generate a payload containing data from the client """
        utcnow = datetime.utcnow()
        data = {
            'exp': utcnow + timedelta(seconds=request.expires_in),
            'nbf': utcnow,
            'iss': 'Odoo',
            'aud': request.client.identifier,
            'iat': utcnow,
            'user_id': request.client.generate_user_id(request.odoo_user),
        }
        if request.client.jwt_scope_id:
            # Sudo as the token's user to execute the scope's filter with that
            # user's rights
            scope = request.client.jwt_scope_id.sudo(user=request.odoo_user)
            scope_data = scope.get_data_for_model(
                'res.users', res_id=request.odoo_user.id)
            # Remove the user id in scope data
            del scope_data['id']
            data.update(scope_data)

        return data

    @api.multi
    def get_oauth2_server(self, validator=None, **kwargs):
        """ Add a custom JWT token generator in the server's arguments """
        self.ensure_one()

        def jwt_generator(request):
            """ Generate a JSON Web Token using a custom payload from the client
            """
            payload = self._generate_jwt_payload(request)
            return jwt.encode(
                payload,
                request.client.jwt_private_key,
                algorithm=request.client.jwt_algorithm,
            )

        # Add the custom generator only if none is already defined
        if self.token_type == 'jwt' and 'token_generator' not in kwargs:
            kwargs['token_generator'] = jwt_generator
            kwargs['refresh_token_generator'] = random_token_generator

        return super(OAuthProviderClient, self).get_oauth2_server(
            validator=validator, **kwargs)
