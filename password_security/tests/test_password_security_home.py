# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import mock

from contextlib import contextmanager

from openerp.tests.common import TransactionCase
from openerp.http import Response

from ..controllers import main


IMPORT = 'openerp.addons.password_security.controllers.main'


class EndTestException(Exception):
    """ It allows for isolation of resources by raise """


class MockResponse(object):
    def __new__(cls):
        return mock.Mock(spec=Response)


class MockPassError(main.PassError):
    def __init__(self):
        super(MockPassError, self).__init__('Message')


class TestPasswordSecurityHome(TransactionCase):

    def setUp(self):
        super(TestPasswordSecurityHome, self).setUp()
        self.PasswordSecurityHome = main.PasswordSecurityHome
        self.password_security_home = self.PasswordSecurityHome()
        self.passwd = 'I am a password!'
        self.qcontext = {
            'password': self.passwd,
        }

    @contextmanager
    def mock_assets(self):
        """ It mocks and returns assets used by this controller """
        methods = ['do_signup', 'web_login', 'web_auth_signup',
                   'web_auth_reset_password',
                   ]
        with mock.patch.multiple(
            main.AuthSignupHome, **{m: mock.DEFAULT for m in methods}
        ) as _super:
            mocks = {}
            for method in methods:
                mocks[method] = _super[method]
                mocks[method].return_value = MockResponse()
            with mock.patch('%s.request' % IMPORT) as request:
                with mock.patch('%s.ensure_db' % IMPORT) as ensure:
                    with mock.patch('%s.http' % IMPORT) as http:
                        http.redirect_with_hash.return_value = \
                            MockResponse()
                        mocks.update({
                            'request': request,
                            'ensure_db': ensure,
                            'http': http,
                        })
                        yield mocks

    def test_do_signup_check(self):
        """ It should check password on user """
        with self.mock_assets() as assets:
            check_password = assets['request'].env.user.check_password
            check_password.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.password_security_home.do_signup(self.qcontext)
            check_password.assert_called_once_with(
                self.passwd,
            )

    def test_do_signup_return(self):
        """ It should return result of super """
        with self.mock_assets() as assets:
            res = self.password_security_home.do_signup(self.qcontext)
            self.assertEqual(assets['do_signup'](), res)

    def test_web_login_ensure_db(self):
        """ It should verify available db """
        with self.mock_assets() as assets:
            assets['ensure_db'].side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.password_security_home.web_login()

    def test_web_login_super(self):
        """ It should call superclass w/ proper args """
        expect_list = [1, 2, 3]
        expect_dict = {'test1': 'good1', 'test2': 'good2'}
        with self.mock_assets() as assets:
            assets['web_login'].side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.password_security_home.web_login(
                    *expect_list, **expect_dict
                )
            assets['web_login'].assert_called_once_with(
                *expect_list, **expect_dict
            )

    def test_web_login_no_post(self):
        """ It should return immediate result of super when not POST """
        with self.mock_assets() as assets:
            assets['request'].httprequest.method = 'GET'
            assets['request'].session.authenticate.side_effect = \
                EndTestException
            res = self.password_security_home.web_login()
            self.assertEqual(
                assets['web_login'](), res,
            )

    def test_web_login_authenticate(self):
        """ It should attempt authentication to obtain uid """
        with self.mock_assets() as assets:
            assets['request'].httprequest.method = 'POST'
            authenticate = assets['request'].session.authenticate
            request = assets['request']
            authenticate.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.password_security_home.web_login()
            authenticate.assert_called_once_with(
                request.session.db,
                request.params['login'],
                request.params['password'],
            )

    def test_web_login_authenticate_fail(self):
        """ It should return super result if failed auth """
        with self.mock_assets() as assets:
            authenticate = assets['request'].session.authenticate
            request = assets['request']
            request.httprequest.method = 'POST'
            request.env['res.users'].sudo.side_effect = EndTestException
            authenticate.return_value = False
            res = self.password_security_home.web_login()
            self.assertEqual(
                assets['web_login'](), res,
            )

    def test_web_login_get_user(self):
        """ It should get the proper user as sudo """
        with self.mock_assets() as assets:
            request = assets['request']
            request.httprequest.method = 'POST'
            sudo = request.env['res.users'].sudo()
            sudo.browse.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.password_security_home.web_login()
            sudo.browse.assert_called_once_with(
                request.uid
            )

    def test_web_login_valid_pass(self):
        """ It should return parent result if pass isn't expired """
        with self.mock_assets() as assets:
            request = assets['request']
            request.httprequest.method = 'POST'
            user = request.env['res.users'].sudo().browse()
            user.action_expire_password.side_effect = EndTestException
            user._password_has_expired.return_value = False
            res = self.password_security_home.web_login()
            self.assertEqual(
                assets['web_login'](), res,
            )

    def test_web_login_expire_pass(self):
        """ It should expire password if necessary """
        with self.mock_assets() as assets:
            request = assets['request']
            request.httprequest.method = 'POST'
            user = request.env['res.users'].sudo().browse()
            user.action_expire_password.side_effect = EndTestException
            user._password_has_expired.return_value = True
            with self.assertRaises(EndTestException):
                self.password_security_home.web_login()

    def test_web_login_redirect(self):
        """ It should redirect w/ hash to reset after expiration """
        with self.mock_assets() as assets:
            request = assets['request']
            request.httprequest.method = 'POST'
            user = request.env['res.users'].sudo().browse()
            user._password_has_expired.return_value = True
            res = self.password_security_home.web_login()
            self.assertEqual(
                assets['http'].redirect_with_hash(), res,
            )

    def test_web_auth_signup_valid(self):
        """ It should return super if no errors """
        with self.mock_assets() as assets:
            res = self.password_security_home.web_auth_signup()
            self.assertEqual(
                assets['web_auth_signup'](), res,
            )

    def test_web_auth_signup_invalid_qcontext(self):
        """ It should catch PassError and get signup qcontext """
        with self.mock_assets() as assets:
            with mock.patch.object(
                main.AuthSignupHome, 'get_auth_signup_qcontext',
            ) as qcontext:
                assets['web_auth_signup'].side_effect = MockPassError
                qcontext.side_effect = EndTestException
                with self.assertRaises(EndTestException):
                    self.password_security_home.web_auth_signup()

    def test_web_auth_signup_invalid_render(self):
        """ It should render & return signup form on invalid """
        with self.mock_assets() as assets:
            with mock.patch.object(
                main.AuthSignupHome, 'get_auth_signup_qcontext', spec=dict
            ) as qcontext:
                assets['web_auth_signup'].side_effect = MockPassError
                res = self.password_security_home.web_auth_signup()
                assets['request'].render.assert_called_once_with(
                    'auth_signup.signup', qcontext(),
                )
                self.assertEqual(
                    assets['request'].render(), res,
                )

    def test_web_auth_reset_password_fail_login(self):
        """ It should raise from failed _validate_pass_reset by login """
        with self.mock_assets() as assets:
            with mock.patch.object(
                main.AuthSignupHome, 'get_auth_signup_qcontext', spec=dict
            ) as qcontext:
                qcontext['login'] = 'login'
                search = assets['request'].env.sudo().search
                assets['request'].httprequest.method = 'POST'
                user = mock.MagicMock()
                user._validate_pass_reset.side_effect = MockPassError
                search.return_value = user
                with self.assertRaises(MockPassError):
                    self.password_security_home.web_auth_reset_password()

    def test_web_auth_reset_password_fail_email(self):
        """ It should raise from failed _validate_pass_reset by email """
        with self.mock_assets() as assets:
            with mock.patch.object(
                main.AuthSignupHome, 'get_auth_signup_qcontext', spec=dict
            ) as qcontext:
                qcontext['login'] = 'login'
                search = assets['request'].env.sudo().search
                assets['request'].httprequest.method = 'POST'
                user = mock.MagicMock()
                user._validate_pass_reset.side_effect = MockPassError
                search.side_effect = [[], user]
                with self.assertRaises(MockPassError):
                    self.password_security_home.web_auth_reset_password()

    def test_web_auth_reset_password_success(self):
        """ It should return parent response on no validate errors """
        with self.mock_assets() as assets:
            with mock.patch.object(
                main.AuthSignupHome, 'get_auth_signup_qcontext', spec=dict
            ) as qcontext:
                qcontext['login'] = 'login'
                assets['request'].httprequest.method = 'POST'
                res = self.password_security_home.web_auth_reset_password()
                self.assertEqual(
                    assets['web_auth_reset_password'](), res,
                )
