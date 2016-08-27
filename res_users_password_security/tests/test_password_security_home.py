# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import mock

from contextlib import contextmanager

from openerp.tests.common import TransactionCase
from openerp.addons.res_users_password_security.controllers import main


IMPORT = 'openerp.addons.res_users_password_security.controllers.main'


class EndTestException(Exception):
    """ It allows for isolation of resources by raise """


class TestPasswordSecurityHome(TransactionCase):

    def setUp(self):
        super(TestPasswordSecurityHome, self).setUp()
        self.Controller = main.PasswordSecurityHome
        self.controller = self.Controller()
        self.passwd = 'I am a password!'
        self.qcontext = {
            'password': self.passwd,
        }

    @contextmanager
    def mock_assets(self):
        """ It mocks and returns assets used by this controller """
        with mock.patch('%s.request' % IMPORT) as request:
            yield {
                'request': request,
            }

    def test_do_signup(self):
        """ It should check password on user """
        with self.mock_assets() as assets:
            check_password = assets['request'].env.user.check_password
            check_password.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.controller.do_signup(self.qcontext)
            check_password.assert_called_once_with(
                self.passwd,
            )
