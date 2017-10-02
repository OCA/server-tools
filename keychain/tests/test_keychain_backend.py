# -*- coding: utf-8 -*-
# © 2016 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.tools.config import config

import logging

_logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet
except ImportError as err:
    _logger.debug(err)


class TestKeychain(TransactionCase):

    def setUp(self):
        super(TestKeychain, self).setUp()

        self.keychain = self.env['keychain.account']
        self.keychain_backend = self.env['keychain.backend']

        def _init_data(self):
            return {
                "c": True,
                "a": "b",
                "d": "",
            }

        def _validate_data(self, data):
            return 'c' in data

        keychain_clss = self.keychain.__class__
        keychain_clss._test_backend_init_data = _init_data
        keychain_clss._test_backend_validate_data = _validate_data

        keychain_backend_clss = self.keychain_backend.__class__
        keychain_backend_clss._backend_name = 'test_backend'

        self.keychain._fields['namespace'].selection.append(
            ('test_backend', 'test backend')
        )

    def test_keychain_bakend(self):
        """It should work with valid data."""
        config['keychain_key_dev'] = Fernet.generate_key()
        config['running_env'] = 'dev'
        vals = {
            'name': 'backend_test',
            'password': 'test',
            'data': '{"a": "o", "c": "b"}'
        }
        # we use new because keychain.backend is an abstract model
        backend = self.keychain_backend.new(vals)
        backend._inverse_keychain()
        account = backend._get_existing_keychain()
        self.assertEqual(
            account.data, '{"a": "o", "c": "b"}',
            'Account data is not correct')
        backend._inverse_password()
        self.assertTrue(account, 'Account was not created')
        self.assertEqual(
            account.clear_password, u'test',
            'Account clear password is not correct')
        self.assertEqual(backend.password, u'test')
        backend._compute_password()
        self.assertEqual(
            backend.password, u'******', 'Backend password was not computed')
        self.assertEqual(
            account.name, u'backend_test dev', 'Account name is not correct')
        self.assertEqual(
            account.namespace, u'test_backend',
            'Account namespace is not correct')
        self.assertEqual(
            account.environment, u'dev', 'Account environment is not correct')
        self.assertEqual(
            account.technical_name, '%s,%s' % (backend._name, backend.id),
            'Account technical_name is not correct')

