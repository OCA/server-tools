# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime
import mock
from openerp.http import Response
from openerp.tests.common import TransactionCase
from ..controllers.main import AuthTotp

CONTROLLER_PATH = 'openerp.addons.auth_totp.controllers.main'
REQUEST_PATH = CONTROLLER_PATH + '.request'
SUPER_PATH = CONTROLLER_PATH + '.Home.web_login'
JSON_PATH = CONTROLLER_PATH + '.JsonSecureCookie'
ENVIRONMENT_PATH = CONTROLLER_PATH + '.Environment'
RESPONSE_PATH = CONTROLLER_PATH + '.Response'
DATETIME_PATH = CONTROLLER_PATH + '.datetime'
TRANSLATE_PATH_CONT = CONTROLLER_PATH + '._'
MODEL_PATH = 'openerp.addons.auth_totp.models.res_users'
GENERATE_PATH = MODEL_PATH + '.ResUsers.generate_mfa_login_token'
VALIDATE_PATH = MODEL_PATH + '.ResUsers.validate_mfa_confirmation_code'
TRANSLATE_PATH_MOD = MODEL_PATH + '._'


@mock.patch(REQUEST_PATH)
class TestAuthTotp(TransactionCase):

    def setUp(self):
        super(TestAuthTotp, self).setUp()

        self.test_controller = AuthTotp()

        self.test_user = self.env.ref('base.user_root')
        self.env['res.users.authenticator'].create({
            'name': 'Test Authenticator',
            'secret_key': 'iamatestsecretyo',
            'user_id': self.test_user.id,
        })
        self.test_user.mfa_enabled = True
        self.test_user.generate_mfa_login_token()
        self.test_user.trusted_device_ids = None

        # Needed when tests are run with no prior requests (e.g. on a new DB)
        patcher = mock.patch('openerp.http.request')
        self.addCleanup(patcher.stop)
        patcher.start()

    @mock.patch(SUPER_PATH)
    def test_web_login_no_password_login(self, super_mock, request_mock):
        '''Should return wrapped result of super if no password log in'''
        test_response = 'Test Response'
        super_mock.return_value = test_response
        request_mock.params = {}

        self.assertEqual(self.test_controller.web_login().data, test_response)

    @mock.patch(SUPER_PATH)
    def test_web_login_user_no_mfa(self, super_mock, request_mock):
        '''Should return wrapped result of super if user did not enable MFA'''
        test_response = 'Test Response'
        super_mock.return_value = test_response
        request_mock.params = {'login_success': True}
        request_mock.env = self.env
        request_mock.uid = self.test_user.id
        self.test_user.mfa_enabled = False

        self.assertEqual(self.test_controller.web_login().data, test_response)

    @mock.patch(JSON_PATH)
    @mock.patch(SUPER_PATH)
    def test_web_login_valid_cookie(self, super_mock, json_mock, request_mock):
        '''Should return wrapped result of super if valid device cookie'''
        test_response = 'Test Response'
        super_mock.return_value = test_response
        request_mock.params = {'login_success': True}
        request_mock.env = self.env
        request_mock.uid = self.test_user.id

        device_model = self.env['res.users.device']
        test_device = device_model.create({'user_id': self.test_user.id})
        json_mock.unserialize().get.return_value = test_device.id

        self.assertEqual(self.test_controller.web_login().data, test_response)

    @mock.patch(SUPER_PATH)
    @mock.patch(GENERATE_PATH)
    def test_web_login_no_cookie(self, gen_mock, super_mock, request_mock):
        '''Should respond correctly if no device cookie with expected key'''
        request_mock.env = self.env
        request_mock.uid = self.test_user.id
        request_mock.params = {
            'login_success': True,
            'redirect': 'Test Redir',
        }
        self.test_user.mfa_login_token = 'Test Token'
        request_mock.httprequest.cookies = {}
        request_mock.reset_mock()

        test_result = self.test_controller.web_login()
        gen_mock.assert_called_once_with()
        request_mock.session.logout.assert_called_once_with(keep_db=True)
        self.assertIn(
            '/auth_totp/login?redirect=Test+Redir&mfa_login_token=Test+Token',
            test_result.data,
        )

    @mock.patch(SUPER_PATH)
    @mock.patch(JSON_PATH)
    @mock.patch(GENERATE_PATH)
    def test_web_login_bad_device_id(
        self, gen_mock, json_mock, super_mock, request_mock
    ):
        '''Should respond correctly if invalid device_id in device cookie'''
        request_mock.env = self.env
        request_mock.uid = self.test_user.id
        request_mock.params = {
            'login_success': True,
            'redirect': 'Test Redir',
        }
        self.test_user.mfa_login_token = 'Test Token'
        json_mock.unserialize.return_value = {'device_id': 1}
        request_mock.reset_mock()

        test_result = self.test_controller.web_login()
        gen_mock.assert_called_once_with()
        request_mock.session.logout.assert_called_once_with(keep_db=True)
        self.assertIn(
            '/auth_totp/login?redirect=Test+Redir&mfa_login_token=Test+Token',
            test_result.data,
        )

    def test_mfa_login_get(self, request_mock):
        '''Should render mfa_login template with correct context'''
        request_mock.render.return_value = 'Test Value'
        request_mock.reset_mock()
        self.test_controller.mfa_login_get()

        request_mock.render.assert_called_once_with(
            'auth_totp.mfa_login',
            qcontext=request_mock.params,
        )

    @mock.patch(TRANSLATE_PATH_MOD)
    def test_mfa_login_post_invalid_token(self, tl_mock, request_mock):
        '''Should return correct redirect if login token invalid'''
        request_mock.env = self.env
        request_mock.params = {
            'mfa_login_token': 'Invalid Token',
            'redirect': 'Test Redir',
        }
        tl_mock.side_effect = lambda arg: arg
        tl_mock.reset_mock()

        test_result = self.test_controller.mfa_login_post()
        tl_mock.assert_called_once()
        self.assertIn('/web/login?redirect=Test+Redir', test_result.data)
        self.assertIn(
            '&error=Your+MFA+login+token+is+not+valid.',
            test_result.data,
        )

    @mock.patch(TRANSLATE_PATH_MOD)
    def test_mfa_login_post_expired_token(self, tl_mock, request_mock):
        '''Should return correct redirect if login token expired'''
        request_mock.env = self.env
        self.test_user.generate_mfa_login_token(-1)
        request_mock.params = {
            'mfa_login_token': self.test_user.mfa_login_token,
            'redirect': 'Test Redir',
        }
        tl_mock.side_effect = lambda arg: arg
        tl_mock.reset_mock()

        test_result = self.test_controller.mfa_login_post()
        tl_mock.assert_called_once()
        self.assertIn('/web/login?redirect=Test+Redir', test_result.data)
        self.assertIn(
            '&error=Your+MFA+login+token+has+expired.',
            test_result.data,
        )

    @mock.patch(TRANSLATE_PATH_CONT)
    def test_mfa_login_post_invalid_conf_code(self, tl_mock, request_mock):
        '''Should return correct redirect if confirmation code is invalid'''
        request_mock.env = self.env
        request_mock.params = {
            'mfa_login_token': self.test_user.mfa_login_token,
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
        self.assertIn(
            '&mfa_login_token=%s' % self.test_user.mfa_login_token,
            test_result.data,
        )

    @mock.patch(GENERATE_PATH)
    @mock.patch(VALIDATE_PATH)
    def test_mfa_login_post_new_token(self, val_mock, gen_mock, request_mock):
        '''Should refresh user's login token w/right lifetime if info valid'''
        request_mock.env = self.env
        request_mock.db = self.registry.db_name
        test_token = self.test_user.mfa_login_token
        request_mock.params = {'mfa_login_token': test_token}
        val_mock.return_value = True
        gen_mock.reset_mock()
        self.test_controller.mfa_login_post()

        gen_mock.assert_called_once_with(60 * 24 * 30)

    @mock.patch(ENVIRONMENT_PATH)
    @mock.patch(VALIDATE_PATH)
    def test_mfa_login_post_session(self, val_mock, env_mock, request_mock):
        '''Should log user in with new token as password if info valid'''
        request_mock.env = self.env
        request_mock.db = self.registry.db_name
        old_test_token = self.test_user.mfa_login_token
        request_mock.params = {'mfa_login_token': old_test_token}
        val_mock.return_value = True
        env_mock.return_value = self.env
        request_mock.reset_mock()
        self.test_controller.mfa_login_post()

        new_test_token = self.test_user.mfa_login_token
        request_mock.session.authenticate.assert_called_once_with(
            request_mock.db,
            self.test_user.login,
            new_test_token,
            self.test_user.id,
        )

    @mock.patch(GENERATE_PATH)
    @mock.patch(VALIDATE_PATH)
    def test_mfa_login_post_redirect(self, val_mock, gen_mock, request_mock):
        '''Should return correct redirect if info valid and redirect present'''
        request_mock.env = self.env
        request_mock.db = self.registry.db_name
        test_redir = 'Test Redir'
        request_mock.params = {
            'mfa_login_token': self.test_user.mfa_login_token,
            'redirect': test_redir,
        }
        val_mock.return_value = True

        test_result = self.test_controller.mfa_login_post()
        self.assertIn("window.location = '%s'" % test_redir, test_result.data)

    @mock.patch(GENERATE_PATH)
    @mock.patch(VALIDATE_PATH)
    def test_mfa_login_post_redir_def(self, val_mock, gen_mock, request_mock):
        '''Should return redirect to /web if info valid and no redirect'''
        request_mock.env = self.env
        request_mock.db = self.registry.db_name
        test_token = self.test_user.mfa_login_token
        request_mock.params = {'mfa_login_token': test_token}
        val_mock.return_value = True

        test_result = self.test_controller.mfa_login_post()
        self.assertIn("window.location = '/web'", test_result.data)

    @mock.patch(GENERATE_PATH)
    @mock.patch(VALIDATE_PATH)
    def test_mfa_login_post_device(self, val_mock, gen_mock, request_mock):
        '''Should add trusted device to user if remember flag set'''
        request_mock.env = self.env
        request_mock.db = self.registry.db_name
        test_token = self.test_user.mfa_login_token
        request_mock.params = {
            'mfa_login_token': test_token,
            'remember_device': True,
        }
        val_mock.return_value = True
        self.test_controller.mfa_login_post()

        self.assertEqual(len(self.test_user.trusted_device_ids), 1)

    @mock.patch(RESPONSE_PATH)
    @mock.patch(JSON_PATH)
    @mock.patch(GENERATE_PATH)
    @mock.patch(VALIDATE_PATH)
    def test_mfa_login_post_cookie_werkzeug_cookie(
        self, val_mock, gen_mock, json_mock, resp_mock, request_mock
    ):
        '''Should create Werkzeug cookie w/right info if remember flag set'''
        request_mock.env = self.env
        request_mock.db = self.registry.db_name
        test_token = self.test_user.mfa_login_token
        request_mock.params = {
            'mfa_login_token': test_token,
            'remember_device': True,
        }
        val_mock.return_value = True
        resp_mock().__class__ = Response
        json_mock.reset_mock()
        self.test_controller.mfa_login_post()

        test_device = self.test_user.trusted_device_ids
        config_model = self.env['ir.config_parameter']
        test_secret = config_model.get_param('database.secret')
        json_mock.assert_called_once_with(
            {'device_id': test_device.id},
            test_secret,
        )

    @mock.patch(DATETIME_PATH)
    @mock.patch(RESPONSE_PATH)
    @mock.patch(JSON_PATH)
    @mock.patch(GENERATE_PATH)
    @mock.patch(VALIDATE_PATH)
    def test_mfa_login_post_cookie_werkzeug_cookie_exp(
        self, val_mock, gen_mock, json_mock, resp_mock, dt_mock, request_mock
    ):
        '''Should serialize Werkzeug cookie w/right exp if remember flag set'''
        request_mock.env = self.env
        request_mock.db = self.registry.db_name
        test_token = self.test_user.mfa_login_token
        request_mock.params = {
            'mfa_login_token': test_token,
            'remember_device': True,
        }
        val_mock.return_value = True
        dt_mock.utcnow.return_value = datetime(2016, 12, 1)
        resp_mock().__class__ = Response
        json_mock.reset_mock()
        self.test_controller.mfa_login_post()

        json_mock().serialize.assert_called_once_with(datetime(2016, 12, 31))

    @mock.patch(DATETIME_PATH)
    @mock.patch(RESPONSE_PATH)
    @mock.patch(JSON_PATH)
    @mock.patch(GENERATE_PATH)
    @mock.patch(VALIDATE_PATH)
    def test_mfa_login_post_cookie_final_cookie(
        self, val_mock, gen_mock, json_mock, resp_mock, dt_mock, request_mock
    ):
        '''Should add correct cookie to response if remember flag set'''
        request_mock.env = self.env
        request_mock.db = self.registry.db_name
        test_token = self.test_user.mfa_login_token
        request_mock.params = {
            'mfa_login_token': test_token,
            'remember_device': True,
        }
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

    @mock.patch(RESPONSE_PATH)
    @mock.patch(GENERATE_PATH)
    @mock.patch(VALIDATE_PATH)
    def test_mfa_login_post_cookie_final_cookie_secure(
        self, val_mock, gen_mock, resp_mock, request_mock
    ):
        '''Should set secure cookie if config parameter set accordingly'''
        request_mock.env = self.env
        request_mock.db = self.registry.db_name
        test_token = self.test_user.mfa_login_token
        request_mock.params = {
            'mfa_login_token': test_token,
            'remember_device': True,
        }
        val_mock.return_value = True
        config_model = self.env['ir.config_parameter']
        config_model.set_param('auth_totp.secure_cookie', '1')
        resp_mock().__class__ = Response
        resp_mock.reset_mock()
        self.test_controller.mfa_login_post()

        new_test_security = resp_mock().set_cookie.mock_calls[0][2]['secure']
        self.assertIs(new_test_security, True)
