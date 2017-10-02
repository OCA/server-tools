# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase
from openerp.tools.config import config
from openerp.exceptions import ValidationError


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
        config['keychain_key'] = Fernet.generate_key()

        self.old_running_env = config.get('running_env', '')
        config['running_env'] = None

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
        keychain_clss._keychain_test_init_data = _init_data
        keychain_clss._keychain_test_validate_data = _validate_data
        keychain_clss._test_backend_validate_data = _validate_data

        keychain_backend_clss = self.keychain_backend.__class__
        keychain_backend_clss._backend_name = 'test_backend'

        self.keychain._fields['namespace'].selection.append(
            ('keychain_test', 'test')
        )
        self.keychain._fields['namespace'].selection.append(
            ('test_backend', 'test backend')
        )

    def tearDown(self):
        config['running_env'] = self.old_running_env
        return super(TestKeychain, self).tearDown()

    def _create_account(self):
        vals = {
            "name": "test",
            "namespace": "keychain_test",
            "login": "test",
            "technical_name": "keychain.test"
        }
        return self.keychain.create(vals)

    def test_password(self):
        """It should encrypt passwords."""
        account = self._create_account()
        passwords = ('', '12345', 'djkqfljfqm', u"""&é"'(§è!ç""")

        for password in passwords:
            account.clear_password = password
            account._inverse_set_password()
            self.assertTrue(account.clear_password != account.password)
            self.assertEqual(account.get_password(), password)

    def test_wrong_key(self):
        """It should raise an exception when encoded key != decoded."""
        account = self._create_account()
        password = 'urieapocq'
        account.clear_password = password
        account._inverse_set_password()
        config['keychain_key'] = Fernet.generate_key()
        try:
            account.get_password()
            self.assertTrue(False, 'It should not work with another key')
        except Warning as err:
            self.assertTrue(True, 'It should raise a Warning')
            self.assertTrue(
                'has been encrypted with a diff' in str(err),
                'It should display the right msg')
        else:
            self.assertTrue(False, 'It should raise a Warning')

    def test_no_key(self):
        """It should raise an exception when no key is set."""
        account = self._create_account()
        del config.options['keychain_key']

        with self.assertRaises(Warning) as err:
            account.clear_password = 'aiuepr'
            account._inverse_set_password()
            self.assertTrue(False, 'It should not work without key')
        self.assertTrue(
            'Use a key similar to' in str(err.exception),
            'It should display the right msg')

    def test_badly_formatted_key(self):
        """It should raise an exception when key is not acceptable format."""
        account = self._create_account()

        config['keychain_key'] = ""
        with self.assertRaises(Warning):
            account.clear_password = 'aiuepr'
            account._inverse_set_password()
            self.assertTrue(False, 'It should not work missing formated key')

        self.assertTrue(True, 'It shoud raise a ValueError')

    def test_retrieve_env(self):
        """Retrieve env should always return False at the end"""
        config['running_env'] = False
        self.assertListEqual(self.keychain._retrieve_env(), [False])

        config['running_env'] = 'dev'
        self.assertListEqual(self.keychain._retrieve_env(), ['dev', False])

        config['running_env'] = 'prod'
        self.assertListEqual(self.keychain._retrieve_env(), ['prod', False])

    def test_multienv(self):
        """Encrypt with dev, decrypt with dev."""
        account = self._create_account()
        config['keychain_key_dev'] = Fernet.generate_key()
        config['keychain_key_prod'] = Fernet.generate_key()
        config['running_env'] = 'dev'

        account.clear_password = 'abc'
        account._inverse_set_password()
        self.assertEqual(
            account.get_password(),
            'abc', 'Should work with dev')

        config['running_env'] = 'prod'
        with self.assertRaises(Warning):
            self.assertEqual(
                account.get_password(),
                'abc', 'Should not work with prod key')

    def test_multienv_blank(self):
        """Encrypt with blank, decrypt for all."""
        account = self._create_account()
        config['keychain_key'] = Fernet.generate_key()
        config['keychain_key_dev'] = Fernet.generate_key()
        config['keychain_key_prod'] = Fernet.generate_key()
        config['running_env'] = ''

        account.clear_password = 'abc'
        account._inverse_set_password()
        self.assertEqual(
            account.get_password(),
            'abc', 'Should work with dev')

        config['running_env'] = 'prod'
        self.assertEqual(
            account.get_password(),
            'abc', 'Should work with prod')

    def test_multienv_force(self):
        """Set the env on the record"""

        account = self._create_account()
        account.environment = 'prod'

        config['keychain_key'] = Fernet.generate_key()
        config['keychain_key_dev'] = Fernet.generate_key()
        config['keychain_key_prod'] = Fernet.generate_key()
        config['running_env'] = ''

        account.clear_password = 'abc'
        account._inverse_set_password()

        with self.assertRaises(Warning):
            self.assertEqual(
                account.get_password(),
                'abc', 'Should not work with dev')

        config['running_env'] = 'prod'
        self.assertEqual(
            account.get_password(),
            'abc', 'Should work with prod')

    def test_wrong_json(self):
        """It should raise an exception when data is not valid json."""
        account = self._create_account()
        wrong_jsons = ("{'hi':'o'}", "{'oq", '[>}')
        for json in wrong_jsons:
            with self.assertRaises(ValidationError) as err:
                account.write({"data": json})
                self.assertTrue(
                    False,
                    'Should not validate baddly formatted json')
            self.assertTrue(
                'Data should be a valid JSON' in str(err.exception),
                'It should raise a ValidationError')

    def test_invalid_json(self):
        """It should raise an exception when data don't pass _validate_data."""
        account = self._create_account()
        invalid_jsons = ('{}', '{"hi": 1}')
        for json in invalid_jsons:
            with self.assertRaises(ValidationError) as err:
                account.write({"data": json})
            self.assertTrue(
                'Data not valid' in str(err.exception),
                'It should raise a ValidationError')

    def test_valid_json(self):
        """It should work with valid data."""
        account = self._create_account()
        valid_jsons = ('{"c": true}', '{"c": 1}', '{"a": "o", "c": "b"}')
        for json in valid_jsons:
            try:
                account.write({"data": json})
                self.assertTrue(True, 'Should validate json')
            except:
                self.assertTrue(False, 'It should validate a good json')

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

