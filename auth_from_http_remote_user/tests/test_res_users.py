# -*- coding: utf-8 -*-
# Copyright 2014-2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from contextlib import contextmanager
import unittest
import mock
from odoo.tests.common import TransactionCase


@contextmanager
def mock_cursor(cr):
    with mock.patch('odoo.sql_db.Connection.cursor') as mocked_cursor_call:
        org_close = cr.close
        org_commit = cr.commit
        try:
            cr.commit = mock.Mock()
            cr.close = mock.Mock()
            mocked_cursor_call.return_value = cr
            yield
        finally:
            cr.close = org_close
            cr.commit = org_commit


class TestResUsers(TransactionCase):

    def test_login(self):
        res_users_obj = self.env['res.users']
        res = res_users_obj.authenticate(
            self.env.cr.dbname, 'demo', 'demo', None)
        self.assertTrue(res, "Basic login must works as expected")
        demo = res_users_obj.browse([res])
        token = "123456"
        res = res_users_obj.authenticate(
            self.env.cr.dbname, 'demo', token, None)
        self.assertFalse(res)
        # mimic what the new controller do when it find a value in
        # the http header (HTTP_REMODE_USER)
        demo.sso_key = token
        # Here we need to mock the cursor since the login is natively done
        # inside its own connection
        with mock_cursor(self.env.cr):
            # We can verifies that the given (id, token) is authorized for
            # the database
            res_users_obj.check(self.env.cr.dbname, demo.id, token)
            # we are able to login with the new token
            res = res_users_obj.authenticate(
                self.env.cr.dbname, 'demo', token, None)
            self.assertTrue(res)

    @unittest.skipIf(os.environ.get('TRAVIS'),
                     'When run by travis, tests runs on a database with all '
                     'required addons from server-tools and their dependencies'
                     ' installed. Even if `auth_from_http_remote_user` does '
                     'not require the `mail` module, The previous installation'
                     ' of the mail module has created the column '
                     '`notification_email_send` as REQUIRED into the table '
                     'res_partner. BTW, it\'s no more possible to copy a '
                     'res_user without an intefirty error')
    def test_copy(self):
        '''Check that the sso_key is not copied on copy
        '''
        self.env.user.sso_key = '123'
        self.assertTrue(self.env.user.sso_key)
        copy = self.env.user.copy()
        self.assertFalse(copy.sso_key)
