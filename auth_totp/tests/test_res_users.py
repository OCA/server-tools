# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime
import mock
import string
from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase
from ..exceptions import (
    MfaTokenError,
    MfaTokenInvalidError,
    MfaTokenExpiredError,
)
from ..models.res_users_authenticator import ResUsersAuthenticator

DATETIME_PATH = 'openerp.addons.auth_totp.models.res_users.datetime'


class TestResUsers(TransactionCase):

    def setUp(self):
        super(TestResUsers, self).setUp()

        self.test_user = self.env.ref('base.user_root')
        self.test_user.mfa_enabled = False
        self.test_user.authenticator_ids = False
        self.env.uid = self.test_user.id

    def test_check_enabled_with_authenticator_mfa_no_auth(self):
        '''Should raise correct error if MFA enabled without authenticators'''
        with self.assertRaisesRegexp(ValidationError, 'locked out'):
            self.test_user.mfa_enabled = True

    def test_check_enabled_with_authenticator_no_mfa_auth(self):
        '''Should not raise error if MFA not enabled with authenticators'''
        try:
            self.env['res.users.authenticator'].create({
                'name': 'Test Name',
                'secret_key': 'Test Key',
                'user_id': self.test_user.id,
            })
        except ValidationError:
            self.fail('A ValidationError was raised and should not have been.')

    def test_check_enabled_with_authenticator_mfa_auth(self):
        '''Should not raise error if MFA enabled with authenticators'''
        try:
            self.env['res.users.authenticator'].create({
                'name': 'Test Name',
                'secret_key': 'Test Key',
                'user_id': self.test_user.id,
            })
            self.test_user.mfa_enabled = True
        except ValidationError:
            self.fail('A ValidationError was raised and should not have been.')

    def test_check_credentials_no_match(self):
        '''Should raise appropriate error if there is no match'''
        with self.assertRaises(MfaTokenInvalidError):
            self.env['res.users'].check_credentials('invalid')

    @mock.patch(DATETIME_PATH)
    def test_check_credentials_expired(self, datetime_mock):
        '''Should raise appropriate error if match based on expired token'''
        datetime_mock.now.return_value = datetime(2016, 12, 1)
        self.test_user.generate_mfa_login_token()
        test_token = self.test_user.mfa_login_token
        datetime_mock.now.return_value = datetime(2017, 12, 1)

        with self.assertRaises(MfaTokenExpiredError):
            self.env['res.users'].check_credentials(test_token)

    def test_check_credentials_current(self):
        '''Should not raise error if match based on active token'''
        self.test_user.generate_mfa_login_token()
        test_token = self.test_user.mfa_login_token

        try:
            self.env['res.users'].check_credentials(test_token)
        except MfaTokenError:
            self.fail('An MfaTokenError was raised and should not have been.')

    def test_generate_mfa_login_token_token_field_content(self):
        '''Should set token field to 20 char string of ASCII letters/digits'''
        self.test_user.generate_mfa_login_token()
        test_chars = set(string.ascii_letters + string.digits)

        self.assertEqual(len(self.test_user.mfa_login_token), 20)
        self.assertTrue(set(self.test_user.mfa_login_token) <= test_chars)

    def test_generate_mfa_login_token_token_field_random(self):
        '''Should set token field to new value each time'''
        test_tokens = set([])
        for __ in xrange(3):
            self.test_user.generate_mfa_login_token()
            test_tokens.add(self.test_user.mfa_login_token)

        self.assertEqual(len(test_tokens), 3)

    @mock.patch(DATETIME_PATH)
    def test_generate_mfa_login_token_exp_field_default(self, datetime_mock):
        '''Should set token lifetime to 15 minutes if no argument provided'''
        datetime_mock.now.return_value = datetime(2016, 12, 1)
        self.test_user.generate_mfa_login_token()

        self.assertEqual(
            self.test_user.mfa_login_token_exp,
            '2016-12-01 00:15:00'
        )

    @mock.patch(DATETIME_PATH)
    def test_generate_mfa_login_token_exp_field_custom(self, datetime_mock):
        '''Should set token lifetime to value provided'''
        datetime_mock.now.return_value = datetime(2016, 12, 1)
        self.test_user.generate_mfa_login_token(45)

        self.assertEqual(
            self.test_user.mfa_login_token_exp,
            '2016-12-01 00:45:00'
        )

    def test_user_from_mfa_login_token_validate_not_singleton(self):
        '''Should raise correct error when recordset is not a singleton'''
        self.test_user.copy()
        test_set = self.env['res.users'].search([('id', '>', 0)], limit=2)

        with self.assertRaises(MfaTokenInvalidError):
            self.env['res.users']._user_from_mfa_login_token_validate()
        with self.assertRaises(MfaTokenInvalidError):
            test_set._user_from_mfa_login_token_validate()

    @mock.patch(DATETIME_PATH)
    def test_user_from_mfa_login_token_validate_expired(self, datetime_mock):
        '''Should raise correct error when record has expired token'''
        datetime_mock.now.return_value = datetime(2016, 12, 1)
        self.test_user.generate_mfa_login_token()
        datetime_mock.now.return_value = datetime(2017, 12, 1)

        with self.assertRaises(MfaTokenExpiredError):
            self.test_user._user_from_mfa_login_token_validate()

    def test_user_from_mfa_login_token_validate_current_singleton(self):
        '''Should not raise error when one record with active token'''
        self.test_user.generate_mfa_login_token()

        try:
            self.test_user._user_from_mfa_login_token_validate()
        except MfaTokenError:
            self.fail('An MfaTokenError was raised and should not have been.')

    def test_user_from_mfa_login_token_match(self):
        '''Should retreive correct user when there is a current match'''
        self.test_user.generate_mfa_login_token()
        test_token = self.test_user.mfa_login_token

        self.assertEqual(
            self.env['res.users'].user_from_mfa_login_token(test_token),
            self.test_user,
        )

    def test_user_from_mfa_login_token_falsy(self):
        '''Should raise correct error when token is falsy'''
        with self.assertRaises(MfaTokenInvalidError):
            self.env['res.users'].user_from_mfa_login_token(None)

    def test_user_from_mfa_login_token_no_match(self):
        '''Should raise correct error when there is no match'''
        with self.assertRaises(MfaTokenInvalidError):
            self.env['res.users'].user_from_mfa_login_token('Test Token')

    @mock.patch(DATETIME_PATH)
    def test_user_from_mfa_login_token_match_expired(self, datetime_mock):
        '''Should raise correct error when the match is expired'''
        datetime_mock.now.return_value = datetime(2016, 12, 1)
        self.test_user.generate_mfa_login_token()
        test_token = self.test_user.mfa_login_token
        datetime_mock.now.return_value = datetime(2017, 12, 1)

        with self.assertRaises(MfaTokenExpiredError):
            self.env['res.users'].user_from_mfa_login_token(test_token)

    def test_validate_mfa_confirmation_code_not_singleton(self):
        '''Should raise correct error when recordset is not singleton'''
        test_user_2 = self.env['res.users']
        test_user_3 = self.env.ref('base.public_user')
        test_set = self.test_user + test_user_3

        with self.assertRaisesRegexp(ValueError, 'Expected singleton'):
            test_user_2.validate_mfa_confirmation_code('Test Code')
        with self.assertRaisesRegexp(ValueError, 'Expected singleton'):
            test_set.validate_mfa_confirmation_code('Test Code')

    @mock.patch.object(ResUsersAuthenticator, 'validate_conf_code')
    def test_validate_mfa_confirmation_code_singleton_return(self, mock_func):
        '''Should return validate_conf_code() value if singleton recordset'''
        mock_func.return_value = 'Test Result'

        self.assertEqual(
            self.test_user.validate_mfa_confirmation_code('Test Code'),
            'Test Result',
        )
