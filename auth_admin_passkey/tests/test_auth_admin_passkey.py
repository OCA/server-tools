# -*- encoding: utf-8 -*-
##############################################################################
#
#    Admin Passkey module for Odoo
#    Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import threading

from openerp.tests.common import TransactionCase


class TestAuthAdminPasskey(TransactionCase):
    """Tests for 'Auth Admin Passkey' Module"""

    # Overload Section
    def setUp(self):
        super(TestAuthAdminPasskey, self).setUp()

        # Get Registries
        self.imd_obj = self.registry('ir.model.data')
        self.ru_obj = self.registry('res.users')

        # Get Database name
        self.db = threading.current_thread().dbname

        # Get ids from xml_ids
        self.admin_user_id = self.imd_obj.get_object_reference(
            self.cr, self.uid, 'base', 'user_root')[1]
        self.demo_user_id = self.imd_obj.get_object_reference(
            self.cr, self.uid, 'base', 'user_demo')[1]

    # Test Section
    def test_01_normal_login_admin_succeed(self):
        """[Regression Test]
        Test the succeed of login with 'admin' / 'admin'"""
        res = self.ru_obj.authenticate(self.db, 'admin', 'admin', {})
        self.assertEqual(
            res, self.admin_user_id,
            "'admin' / 'admin' login must succeed.")

    def test_02_normal_login_admin_fail(self):
        """[Regression Test]
        Test the fail of login with 'admin' / 'bad_password'"""
        res = self.ru_obj.authenticate(self.db, 'admin', 'bad_password', {})
        self.assertEqual(
            res, False,
            "'admin' / 'bad_password' login must fail.")

    def test_03_normal_login_demo_succeed(self):
        """[Regression Test]
        Test the succeed of login with 'demo' / 'demo'"""
        res = self.ru_obj.authenticate(self.db, 'demo', 'demo', {})
        self.assertEqual(
            res, self.demo_user_id,
            "'demo' / 'demo' login must succeed.")

    def test_04_normal_login_demo_fail(self):
        """[Regression Test]
        Test the fail of login with 'demo' / 'bad_password'"""
        res = self.ru_obj.authenticate(self.db, 'demo', 'bad_password', {})
        self.assertEqual(
            res, False,
            "'demo' / 'bad_password' login must fail.")

    def test_05_passkey_login_demo_succeed(self):
        """[New Feature]
        Test the succeed of login with 'demo' / 'admin'"""
        res = self.ru_obj.authenticate(self.db, 'demo', 'admin', {})
        self.assertEqual(
            res, self.demo_user_id,
            "'demo' / 'admin' login must succeed.")

    def test_06_passkey_login_demo_succeed(self):
        """[Bug #1319391]
        Test the correct behaviour of login with 'bad_login' / 'admin'"""
        exception_raised = False
        try:
            self.ru_obj.authenticate(self.db, 'bad_login', 'admin', {})
        except:
            exception_raised = True
        self.assertEqual(
            exception_raised, False,
            "'bad_login' / 'admin' musn't raise Error.")
