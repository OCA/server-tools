# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from xmlrpc.client import Fault

from mock import patch
from werkzeug.utils import redirect

from odoo import http
from odoo.tests.common import at_install, HttpCase, post_install


@at_install(False)
@post_install(True)
# Skip CSRF validation on tests
@patch(http.__name__ + ".WebRequest.validate_csrf", return_value=True)
# Skip specific browser forgery on redirections
@patch(http.__name__ + ".redirect_with_hash", side_effect=redirect)
class TestRemote(HttpCase):
    def setUp(self):
        super().setUp()
        # HACK https://github.com/odoo/odoo/issues/24183
        # TODO Remove in v12
        # Complex password to avoid conflicts with `password_security`
        self.good_password = "Admin$%02584"
        self.data_demo = {
            "login": "demo",
            "password": "Demo%&/(908409**",
        }
        self.remote_addr = '127.0.0.1'
        with self.cursor() as cr:
            env = self.env(cr)
            # Make sure involved users have good passwords
            env.user.password = self.good_password
            env["res.users"].search([
                ("login", "=", self.data_demo["login"]),
            ]).password = self.data_demo["password"]
            remote = self.env['res.remote'].search([
                ('ip', '=', self.remote_addr)
            ])
            if remote:
                remote.unlink()

    def test_xmlrpc_login_ok(self, *args):
        """Test Login"""
        data1 = self.data_demo
        self.assertTrue(self.xmlrpc_common.authenticate(
            self.env.cr.dbname, data1["login"], data1["password"], {}))
        with self.cursor() as cr:
            env = self.env(cr)
            self.assertTrue(
                env['res.remote'].search([('ip', '=', self.remote_addr)])
            )

    def test_xmlrpc_login_failure(self, *args):
        """Test Login Failure"""
        data1 = self.data_demo
        data1['password'] = 'Failure!'
        self.assertFalse(self.xmlrpc_common.authenticate(
            self.env.cr.dbname, data1["login"], data1["password"], {}))
        with self.cursor() as cr:
            env = self.env(cr)
            self.assertTrue(
                env['res.remote'].search([('ip', '=', self.remote_addr)])
            )
