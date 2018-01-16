# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from datetime import datetime
from mock import patch
from odoo.fields import Datetime
from odoo.tests.common import TransactionCase
from ..controllers.main import AuthTotpPasswordSecurity

CONTROLLER_PATH = 'odoo.addons.auth_totp_password_security.controllers.main'
MODEL_PATH = 'odoo.addons.password_security.models.res_users.ResUsers'


@patch(CONTROLLER_PATH + '.AuthTotp.mfa_login_post')
class TestAuthTotpPasswordSecurity(TransactionCase):

    def setUp(self):
        super(TestAuthTotpPasswordSecurity, self).setUp()

        self.test_controller = AuthTotpPasswordSecurity()

        self.test_user = self.env.ref('base.user_root')
        self.test_user.company_id.password_expiration = 1
        pass_date = datetime(year=2016, month=1, day=1)
        self.test_user.password_write_date = Datetime.to_string(pass_date)

        request_patcher = patch(CONTROLLER_PATH + '.request')
        self.addCleanup(request_patcher.stop)
        self.request_mock = request_patcher.start()
        self.request_mock.params = {'login_success': True}
        self.request_mock.uid = self.test_user.id
        self.request_mock.env = self.env

        # Needed when tests are run with no prior requests
        base_request_patcher = patch('odoo.http.request')
        self.addCleanup(base_request_patcher.stop)
        base_request_patcher.start()

    def test_mfa_login_post_no_mfa_login(self, super_mock):
        """Should return result of super if MFA login not complete"""
        test_response = 'Test Response'
        super_mock.return_value = test_response
        self.request_mock.params = {}
        result = self.test_controller.mfa_login_post().get_data()

        self.assertEqual(result, test_response)

    def test_mfa_login_post_pass_not_expired(self, super_mock):
        """Should return result of super if user's password not expired"""
        test_response = 'Test Response'
        super_mock.return_value = test_response
        self.test_user.password_write_date = Datetime.to_string(datetime.now())
        result = self.test_controller.mfa_login_post().get_data()

        self.assertEqual(result, test_response)

    @patch(MODEL_PATH + '.action_expire_password')
    def test_mfa_login_post_expired_helper(self, helper_mock, super_mock):
        """Should correctly call helper if user's password is expired"""
        self.test_controller.mfa_login_post()

        helper_mock.assert_called_once_with()

    def test_mfa_login_post_expired_log_out(self, super_mock):
        """Should log out user and update params if password is expired"""
        self.test_controller.mfa_login_post()

        self.request_mock.session.logout.assert_called_once_with(keep_db=True)
        self.assertFalse(self.request_mock.params['login_success'])

    def test_mfa_login_post_expired_redirect(self, super_mock):
        """Should return correct redirect if password is expired"""
        result = self.test_controller.mfa_login_post().get_data()

        expected = self.test_user.partner_id.signup_url
        self.assertIn(expected, result)
