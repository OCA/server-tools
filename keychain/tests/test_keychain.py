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
        config['keychain_key'] = Fernet.generate_key()

        def _init_data(self):
            return {
                "c": True,
                "a": "b",
                "d": "",
            }

        def _validate_data(self, data):
            return 'c' in data

        keychain_clss = self.keychain.__class__
        keychain_clss._keychain_test_init_data = _init_data
        keychain_clss._keychain_test_validate_data = _validate_data

        self.keychain._fields['namespace'].selection.append(
            ('keychain_test', 'test')
        )

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
            account._set_password()
            self.assertTrue(account.clear_password != account.password)
            self.assertEqual(account.get_password(), password)

    def test_wrong_key(self):
        """It should raise an exception when encoded key != decoded."""
        account = self._create_account()
        password = 'urieapocq'
        account.clear_password = password
        account._set_password()
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
        try:
            account.clear_password = 'aiuepr'
            account._set_password()
            self.assertTrue(False, 'It should not work without key')
        except Warning as err:
            self.assertTrue(True, 'It should raise a Warning')
            self.assertTrue(
                'Use a key like' in str(err),
                'It should display the right msg')
        else:
            self.assertTrue(False, 'It should raise a Warning')

    def test_badly_formatted_key(self):
        """It should raise an exception when key is not acceptable format."""
        account = self._create_account()

        config['keychain_key'] = ""
        try:
            account.clear_password = 'aiuepr'
            account._set_password()
            self.assertTrue(False, 'It should not work baddly formated key')
        except ValueError:
            self.assertTrue(True, 'It shoud raise a ValueError')
        else:
            self.assertTrue(False, 'It should raise a ValueError')

    def test_wrong_json(self):
        """It should raise an exception when data is not valid json."""
        account = self._create_account()
        wrong_jsons = ("{'hi':'o'}", "{'oq", '[>}')
        for json in wrong_jsons:
            try:
                account.write({"data": json})
                self.assertTrue(
                    False,
                    'Should not validate baddly formatted json')
            except ValidationError as err:
                self.assertTrue(
                    'Data not valid JSON' in err.args[1],
                    'It should raise a ValidationError')
            else:
                self.assertTrue(
                    False,
                    'It should raise a ValidationError')

    def test_invalid_json(self):
        """It should raise an exception when data don't pass _validate_data."""
        account = self._create_account()
        invalid_jsons = ('{}', '{"hi": 1}')
        for json in invalid_jsons:
            try:
                account.write({"data": json})
                self.assertTrue(
                    False,
                    'Should not validate semantically wrong json')
            except ValidationError as err:
                self.assertTrue(
                    'Data not valid' in str(err),
                    'It should raise a ValidationError')
            else:
                self.assertTrue(
                    False,
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
