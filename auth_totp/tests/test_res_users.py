# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from mock import patch
from odoo.exceptions import AccessDenied, ValidationError
from odoo.tests.common import TransactionCase
from ..exceptions import MfaLoginNeeded
from ..models.res_users import JsonSecureCookie
from ..models.res_users_authenticator import ResUsersAuthenticator

MODEL_PATH = 'odoo.addons.auth_totp.models.res_users'
REQUEST_PATH = MODEL_PATH + '.request'


class TestResUsers(TransactionCase):

    def setUp(self):
        super(TestResUsers, self).setUp()

        self.test_user = self.env.ref('base.user_root')
        self.test_user.mfa_enabled = False
        self.test_user.authenticator_ids = False
        self.env['res.users.authenticator'].create({
            'name': 'Test Name',
            'secret_key': 'Test Key',
            'user_id': self.test_user.id,
        })
        self.test_user.mfa_enabled = True

        self.env.uid = self.test_user.id

    def test_compute_trusted_device_cookie_key_disable_mfa(self):
        """It should clear out existing key when MFA is disabled"""
        self.test_user.mfa_enabled = False

        self.assertFalse(self.test_user.trusted_device_cookie_key)

    def test_compute_trusted_device_cookie_key_enable_mfa(self):
        """It should generate a new key when MFA is enabled"""
        old_key = self.test_user.trusted_device_cookie_key
        self.test_user.mfa_enabled = False
        self.test_user.mfa_enabled = True

        self.assertNotEqual(self.test_user.trusted_device_cookie_key, old_key)

    def test_build_model_mfa_fields_in_self_writeable_list(self):
        '''Should add MFA fields to list of fields users can modify for self'''
        ResUsersClass = type(self.test_user)
        self.assertIn('mfa_enabled', ResUsersClass.SELF_WRITEABLE_FIELDS)
        self.assertIn('authenticator_ids', ResUsersClass.SELF_WRITEABLE_FIELDS)

    def test_check_enabled_with_authenticator_mfa_no_auth(self):
        '''Should raise correct error if MFA enabled without authenticators'''
        with self.assertRaisesRegexp(ValidationError, 'locked out'):
            self.test_user.authenticator_ids = False

    def test_check_enabled_with_authenticator_no_mfa_auth(self):
        '''Should not raise error if MFA not enabled with authenticators'''
        try:
            self.test_user.mfa_enabled = False
        except ValidationError:
            self.fail('A ValidationError was raised and should not have been.')

    def test_check_credentials_mfa_not_enabled(self):
        '''Should check password if user does not have MFA enabled'''
        self.test_user.mfa_enabled = False

        with self.assertRaises(AccessDenied):
            self.env['res.users'].check_credentials('invalid')
        try:
            self.env['res.users'].check_credentials('admin')
        except AccessDenied:
            self.fail('An exception was raised with a correct password.')

    @patch(REQUEST_PATH, new=None)
    def test_check_credentials_mfa_and_no_request(self):
        '''Should raise correct exception if MFA enabled and no request'''
        with self.assertRaises(AccessDenied):
            self.env['res.users'].check_credentials('invalid')
        with self.assertRaises(MfaLoginNeeded):
            self.env['res.users'].check_credentials('admin')

    @patch(REQUEST_PATH)
    def test_check_credentials_mfa_login_active(self, request_mock):
        '''Should check password if user has finished MFA auth this session'''
        request_mock.session = {'mfa_login_active': self.test_user.id}

        with self.assertRaises(AccessDenied):
            self.env['res.users'].check_credentials('invalid')
        try:
            self.env['res.users'].check_credentials('admin')
        except AccessDenied:
            self.fail('An exception was raised with a correct password.')

    @patch(REQUEST_PATH)
    def test_check_credentials_mfa_different_login_active(self, request_mock):
        '''Should correctly raise/update if other user finished MFA auth'''
        request_mock.session = {'mfa_login_active': self.test_user.id + 1}
        request_mock.httprequest.cookies = {}

        with self.assertRaises(AccessDenied):
            self.env['res.users'].check_credentials('invalid')
        self.assertFalse(request_mock.session.get('mfa_login_needed'))
        with self.assertRaises(MfaLoginNeeded):
            self.env['res.users'].check_credentials('admin')
        self.assertTrue(request_mock.session.get('mfa_login_needed'))

    @patch(REQUEST_PATH)
    def test_check_credentials_mfa_no_device_cookie(self, request_mock):
        '''Should correctly raise/update session if MFA and no device cookie'''
        request_mock.session = {'mfa_login_active': False}
        request_mock.httprequest.cookies = {}

        with self.assertRaises(AccessDenied):
            self.env['res.users'].check_credentials('invalid')
        self.assertFalse(request_mock.session.get('mfa_login_needed'))
        with self.assertRaises(MfaLoginNeeded):
            self.env['res.users'].check_credentials('admin')
        self.assertTrue(request_mock.session.get('mfa_login_needed'))

    @patch(REQUEST_PATH)
    def test_check_credentials_mfa_corrupted_device_cookie(self, request_mock):
        '''Should correctly raise/update session if MFA and corrupted cookie'''
        request_mock.session = {'mfa_login_active': False}
        test_key = 'trusted_devices_%d' % self.test_user.id
        request_mock.httprequest.cookies = {test_key: 'invalid'}

        with self.assertRaises(AccessDenied):
            self.env['res.users'].check_credentials('invalid')
        self.assertFalse(request_mock.session.get('mfa_login_needed'))
        with self.assertRaises(MfaLoginNeeded):
            self.env['res.users'].check_credentials('admin')
        self.assertTrue(request_mock.session.get('mfa_login_needed'))

    @patch(REQUEST_PATH)
    def test_check_credentials_mfa_cookie_from_wrong_user(self, request_mock):
        '''Should raise and update session if MFA and wrong user's cookie'''
        request_mock.session = {'mfa_login_active': False}
        test_user_2 = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
        })
        test_id_2 = test_user_2.id
        self.env['res.users.authenticator'].create({
            'name': 'Test Name',
            'secret_key': 'Test Key',
            'user_id': test_id_2,
        })
        test_user_2.mfa_enabled = True
        secret = test_user_2.trusted_device_cookie_key
        test_device_cookie = JsonSecureCookie({'user_id': test_id_2}, secret)
        test_device_cookie = test_device_cookie.serialize()
        test_key = 'trusted_devices_%d' % self.test_user.id
        request_mock.httprequest.cookies = {test_key: test_device_cookie}

        with self.assertRaises(AccessDenied):
            self.env['res.users'].check_credentials('invalid')
        self.assertFalse(request_mock.session.get('mfa_login_needed'))
        with self.assertRaises(MfaLoginNeeded):
            self.env['res.users'].check_credentials('admin')
        self.assertTrue(request_mock.session.get('mfa_login_needed'))

    @patch(REQUEST_PATH)
    def test_check_credentials_mfa_correct_device_cookie(self, request_mock):
        '''Should check password if MFA and correct device cookie'''
        request_mock.session = {'mfa_login_active': False}
        secret = self.test_user.trusted_device_cookie_key
        test_device_cookie = JsonSecureCookie(
            {'user_id': self.test_user.id},
            secret,
        )
        test_device_cookie = test_device_cookie.serialize()
        test_key = 'trusted_devices_%d' % self.test_user.id
        request_mock.httprequest.cookies = {test_key: test_device_cookie}

        with self.assertRaises(AccessDenied):
            self.env['res.users'].check_credentials('invalid')
        try:
            self.env['res.users'].check_credentials('admin')
        except AccessDenied:
            self.fail('An exception was raised with a correct password.')

    def test_validate_mfa_confirmation_code_not_singleton(self):
        '''Should raise correct error when recordset is not singleton'''
        test_user_2 = self.env['res.users']
        test_user_3 = self.env.ref('base.public_user')
        test_set = self.test_user + test_user_3

        with self.assertRaisesRegexp(ValueError, 'Expected singleton'):
            test_user_2.validate_mfa_confirmation_code('Test Code')
        with self.assertRaisesRegexp(ValueError, 'Expected singleton'):
            test_set.validate_mfa_confirmation_code('Test Code')

    @patch.object(ResUsersAuthenticator, 'validate_conf_code')
    def test_validate_mfa_confirmation_code_singleton_return(self, mock_func):
        '''Should return validate_conf_code() value if singleton recordset'''
        mock_func.return_value = 'Test Result'

        self.assertEqual(
            self.test_user.validate_mfa_confirmation_code('Test Code'),
            'Test Result',
        )
