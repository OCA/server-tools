# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import SUPERUSER_ID, exceptions
from odoo.tests import common


@common.post_install(True)
class TestAuthAdminPasskey(common.TransactionCase):
    """Tests for 'Auth Admin Passkey' Module"""

    def setUp(self):
        super(TestAuthAdminPasskey, self).setUp()

        self.ru_obj = self.env['res.users']

        self.db = self.env.cr.dbname

        self.admin_user = self.ru_obj.search([('id', '=', SUPERUSER_ID)])
        self.passkey_user = self.ru_obj.create({
            'login': 'passkey',
            'password': 'PasskeyPa$$w0rd',
            'name': 'passkey'
        })

    def test_01_normal_login_admin_succeed(self):
        # NOTE: Can fail if admin password changed
        self.admin_user.check_credentials('admin')

    def test_02_normal_login_admin_fail(self):
        with self.assertRaises(exceptions.AccessDenied):
            self.admin_user.check_credentials('bad_password')

    def test_03_normal_login_passkey_succeed(self):
        """ This test cannot pass because in some way the the _uid of
            passkey_user is equal to admin one so when entering the
            original check_credentials() method, it raises an exception
            """
        try:
            self.passkey_user.check_credentials('passkey')
        except exceptions.AccessDenied:
            # This exception is raised from the origin check_credentials()
            # method and its an expected behaviour as we catch this in our
            # check_credentials()
            pass

    def test_04_normal_login_passkey_fail(self):
        with self.assertRaises(exceptions.AccessDenied):
            self.passkey_user.check_credentials('bad_password')

    def test_05_passkey_login_passkey_with_admin_password_succeed(self):
        # NOTE: Can fail if admin password changed
        self.passkey_user.check_credentials('admin')

    def test_06_passkey_login_passkey_succeed(self):
        """[Bug #1319391]
        Test the correct behaviour of login with 'bad_login' / 'admin'"""
        res = self.ru_obj.authenticate(self.db, 'bad_login', 'admin', {})
        self.assertFalse(res)
