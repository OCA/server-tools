# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime
from mock import MagicMock, patch
from odoo.http import Response
from odoo.tests.common import TransactionCase
from ..controllers.main import AuthTotp

CONTROLLER_PATH = 'odoo.addons.auth_totp.controllers.main'
REQUEST_PATH = CONTROLLER_PATH + '.request'
SUPER_PATH = CONTROLLER_PATH + '.Home.web_login'
JSON_PATH = CONTROLLER_PATH + '.JsonSecureCookie'
RESPONSE_PATH = CONTROLLER_PATH + '.Response'
DATETIME_PATH = CONTROLLER_PATH + '.datetime'
REDIRECT_PATH = CONTROLLER_PATH + '.http.redirect_with_hash'
TRANSLATE_PATH_CONT = CONTROLLER_PATH + '._'
MODEL_PATH = 'odoo.addons.auth_totp.models.res_users'
VALIDATE_PATH = MODEL_PATH + '.ResUsers.validate_mfa_confirmation_code'


class AssignableDict(dict):
    pass


@patch(REQUEST_PATH)
class TestAuthTotp(TransactionCase):

    def setUp(self):
        super(TestAuthTotp, self).setUp()

        self.test_controller = AuthTotp()

        self.test_user = self.env.ref('base.user_root')
        self.test_user.mfa_enabled = False
        self.test_user.authenticator_ids = False
        self.env['res.users.authenticator'].create({
            'name': 'Test Authenticator',
            'secret_key': 'iamatestsecretyo',
            'user_id': self.test_user.id,
        })
        self.test_user.mfa_enabled = True

        # Needed when tests are run with no prior requests (e.g. on a new DB)
        patcher = patch('odoo.http.request')
        self.addCleanup(patcher.stop)
        patcher.start()

    @patch(SUPER_PATH)
    def test_web_login_mfa_needed(self, super_mock, request_mock):
        '''Should update session and redirect correctly if MFA login needed'''
        request_mock.session = {'mfa_login_needed': True}
        request_mock.params = {'redirect': 'Test Redir'}

        test_result = self.test_controller.web_login()
        super_mock.assert_called_once()
        self.assertIn('/auth_totp/login?redirect=Test+Redir', test_result.data)
        self.assertFalse(request_mock.session['mfa_login_needed'])

    @patch(SUPER_PATH)
    def test_web_login_mfa_not_needed(self, super_mock, request_mock):
        '''Should return result of calling super if MFA login not needed'''
        test_response = 'Test Response'
        super_mock.return_value = test_response
        request_mock.session = {}

        self.assertEqual(self.test_controller.web_login().data, test_response)

    def test_mfa_login_get(self, request_mock):
        '''Should render mfa_login template with correct context'''
        request_mock.render.return_value = 'Test Value'
        request_mock.reset_mock()
        self.test_controller.mfa_login_get()

        request_mock.render.assert_called_once_with(
            'auth_totp.mfa_login',
            qcontext=request_mock.params,
        )

    @patch(TRANSLATE_PATH_CONT)
    def test_mfa_login_post_no_login(self, tl_mock, request_mock):
        '''Should redirect correctly if login missing from session'''
        request_mock.env = self.env
        request_mock.session = {}
        request_mock.params = {'redirect': 'Test Redir'}
        tl_mock.side_effect = lambda arg: arg
        tl_mock.reset_mock()

        test_result = self.test_controller.mfa_login_post()
        tl_mock.assert_called_once()
        self.assertIn('/web/login?redirect=Test+Redir', test_result.data)
        self.assertIn('&error=You+must+log+in', test_result.data)

    @patch(TRANSLATE_PATH_CONT)
    def test_mfa_login_post_invalid_login(self, tl_mock, request_mock):
        '''Should redirect correctly if invalid login in session'''
        request_mock.env = self.env
        request_mock.session = {'login': 'Invalid Login'}
        request_mock.params = {'redirect': 'Test Redir'}
        tl_mock.side_effect = lambda arg: arg
        tl_mock.reset_mock()

        test_result = self.test_controller.mfa_login_post()
        tl_mock.assert_called_once()
        self.assertIn('/web/login?redirect=Test+Redir', test_result.data)
        self.assertIn('&error=You+must+log+in', test_result.data)

    @patch(TRANSLATE_PATH_CONT)
    def test_mfa_login_post_invalid_conf_code(self, tl_mock, request_mock):
        '''Should return correct redirect if confirmation code is invalid'''
        request_mock.env = self.env
        request_mock.session = {'login': self.test_user.login}
        request_mock.params = {
            'redirect': 'Test Redir',
            'confirmation_code': 'Invalid Code',
        }
        tl_mock.side_effect = lambda arg: arg
        tl_mock.reset_mock()

        test_result = self.test_controller.mfa_login_post()
        tl_mock.assert_called_once()
        self.assertIn('/auth_totp/login?redirect=Test+Redir', test_result.data)
        self.assertIn(
            '&error=Your+confirmation+code+is+not+correct.',
            test_result.data,
        )

    @patch(VALIDATE_PATH)
    def test_mfa_login_post_valid_conf_code(self, val_mock, request_mock):
        '''Should correctly update session if confirmation code is valid'''
        request_mock.env = self.env
        request_mock.session = AssignableDict(login=self.test_user.login)
        request_mock.session.authenticate = MagicMock()
        test_conf_code = 'Test Code'
        request_mock.params = {'confirmation_code': test_conf_code}
        val_mock.return_value = True
        self.test_controller.mfa_login_post()

        val_mock.assert_called_once_with(test_conf_code)
        resulting_flag = request_mock.session['mfa_login_active']
        self.assertEqual(resulting_flag, self.test_user.id)

    @patch(VALIDATE_PATH)
    def test_mfa_login_post_pass_auth_fail(self, val_mock, request_mock):
        '''Should not set success param if password auth fails'''
        request_mock.env = self.env
        request_mock.db = test_db = 'Test DB'
        test_password = 'Test Password'
        request_mock.session = AssignableDict(
            login=self.test_user.login, password=test_password,
        )
        request_mock.session.authenticate = MagicMock(return_value=False)
        request_mock.params = {}
        val_mock.return_value = True
        self.test_controller.mfa_login_post()

        request_mock.session.authenticate.assert_called_once_with(
            test_db, self.test_user.login, test_password,
        )
        self.assertFalse(request_mock.params.get('login_success'))

    @patch(VALIDATE_PATH)
    def test_mfa_login_post_pass_auth_success(self, val_mock, request_mock):
        '''Should set success param if password auth succeeds'''
        request_mock.env = self.env
        request_mock.db = test_db = 'Test DB'
        test_password = 'Test Password'
        request_mock.session = AssignableDict(
            login=self.test_user.login, password=test_password,
        )
        request_mock.session.authenticate = MagicMock(return_value=True)
        request_mock.params = {}
        val_mock.return_value = True
        self.test_controller.mfa_login_post()

        request_mock.session.authenticate.assert_called_once_with(
            test_db, self.test_user.login, test_password,
        )
        self.assertTrue(request_mock.params.get('login_success'))

    @patch(VALIDATE_PATH)
    def test_mfa_login_post_redirect(self, val_mock, request_mock):
        '''Should return correct redirect if info valid and redirect present'''
        request_mock.env = self.env
        request_mock.session = AssignableDict(login=self.test_user.login)
        request_mock.session.authenticate = MagicMock(return_value=True)
        test_redir = 'Test Redir'
        request_mock.params = {'redirect': test_redir}
        val_mock.return_value = True

        test_result = self.test_controller.mfa_login_post()
        self.assertIn("window.location = '%s'" % test_redir, test_result.data)

    @patch(VALIDATE_PATH)
    def test_mfa_login_post_redir_def(self, val_mock, request_mock):
        '''Should return redirect to /web if info valid and no redirect'''
        request_mock.env = self.env
        request_mock.session = AssignableDict(login=self.test_user.login)
        request_mock.session.authenticate = MagicMock(return_value=True)
        request_mock.params = {}
        val_mock.return_value = True

        test_result = self.test_controller.mfa_login_post()
        self.assertIn("window.location = '/web'", test_result.data)

    @patch(RESPONSE_PATH)
    @patch(JSON_PATH)
    @patch(VALIDATE_PATH)
    def test_mfa_login_post_cookie_werkzeug_cookie(
        self, val_mock, json_mock, resp_mock, request_mock
    ):
        '''Should create Werkzeug cookie w/right info if remember flag set'''
        request_mock.env = self.env
        request_mock.session = AssignableDict(login=self.test_user.login)
        request_mock.session.authenticate = MagicMock(return_value=True)
        request_mock.params = {'remember_device': True}
        val_mock.return_value = True
        resp_mock().__class__ = Response
        json_mock.reset_mock()
        self.test_controller.mfa_login_post()

        test_secret = self.test_user.trusted_device_cookie_key
        json_mock.assert_called_once_with(
            {'user_id': self.test_user.id},
            test_secret,
        )

    @patch(DATETIME_PATH)
    @patch(RESPONSE_PATH)
    @patch(JSON_PATH)
    @patch(VALIDATE_PATH)
    def test_mfa_login_post_cookie_werkzeug_cookie_exp(
        self, val_mock, json_mock, resp_mock, dt_mock, request_mock
    ):
        '''Should serialize Werkzeug cookie w/right exp if remember flag set'''
        request_mock.env = self.env
        request_mock.session = AssignableDict(login=self.test_user.login)
        request_mock.session.authenticate = MagicMock(return_value=True)
        request_mock.params = {'remember_device': True}
        val_mock.return_value = True
        dt_mock.utcnow.return_value = datetime(2016, 12, 1)
        resp_mock().__class__ = Response
        json_mock.reset_mock()
        self.test_controller.mfa_login_post()

        json_mock().serialize.assert_called_once_with(datetime(2016, 12, 31))

    @patch(DATETIME_PATH)
    @patch(RESPONSE_PATH)
    @patch(JSON_PATH)
    @patch(VALIDATE_PATH)
    def test_mfa_login_post_cookie_final_cookie(
        self, val_mock, json_mock, resp_mock, dt_mock, request_mock
    ):
        '''Should add correct cookie to response if remember flag set'''
        request_mock.env = self.env
        request_mock.session = AssignableDict(login=self.test_user.login)
        request_mock.session.authenticate = MagicMock(return_value=True)
        request_mock.params = {'remember_device': True}
        val_mock.return_value = True
        dt_mock.utcnow.return_value = datetime(2016, 12, 1)
        config_model = self.env['ir.config_parameter']
        config_model.set_param('auth_totp.secure_cookie', '0')
        resp_mock().__class__ = Response
        resp_mock.reset_mock()
        self.test_controller.mfa_login_post()

        resp_mock().set_cookie.assert_called_once_with(
            'trusted_devices_%s' % self.test_user.id,
            json_mock().serialize(),
            max_age=30 * 24 * 60 * 60,
            expires=datetime(2016, 12, 31),
            httponly=True,
            secure=False,
        )

    @patch(RESPONSE_PATH)
    @patch(VALIDATE_PATH)
    def test_mfa_login_post_cookie_final_cookie_secure(
        self, val_mock, resp_mock, request_mock
    ):
        '''Should set secure cookie if config parameter set accordingly'''
        request_mock.env = self.env
        request_mock.session = AssignableDict(login=self.test_user.login)
        request_mock.session.authenticate = MagicMock(return_value=True)
        request_mock.params = {'remember_device': True}
        val_mock.return_value = True
        config_model = self.env['ir.config_parameter']
        config_model.set_param('auth_totp.secure_cookie', '1')
        resp_mock().__class__ = Response
        resp_mock.reset_mock()
        self.test_controller.mfa_login_post()

        new_test_security = resp_mock().set_cookie.mock_calls[0][2]['secure']
        self.assertIs(new_test_security, True)

    @patch(REDIRECT_PATH)
    @patch(VALIDATE_PATH)
    def test_mfa_login_post_firefox_response_returned(
        self, val_mock, redirect_mock, request_mock
    ):
        '''Should behave well if redirect returns Response (Firefox case)'''
        request_mock.env = self.env
        request_mock.session = AssignableDict(login=self.test_user.login)
        request_mock.session.authenticate = MagicMock(return_value=True)
        redirect_mock.return_value = Response('Test Response')
        val_mock.return_value = True

        test_result = self.test_controller.mfa_login_post()
        self.assertIn('Test Response', test_result.response)
