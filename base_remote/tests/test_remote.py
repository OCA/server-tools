# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import http
from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
# Skip CSRF validation on tests
@patch(http.__name__ + ".Request.validate_csrf", return_value=True)
class TestRemote(HttpCase):
    def setUp(self):
        super().setUp()

        # Complex password to avoid conflicts with `password_security`
        self.good_password = "Admin$%02584"
        self.data_demo = {
            "login": "demo",
            "password": "Demo%&/(908409**",
        }
        self.remote_addr = "127.0.0.1"
        with self.cursor() as cr:
            env = self.env(cr)
            # Make sure involved users have good passwords
            env.user.password = self.good_password
            env["res.users"].search(
                [("login", "=", self.data_demo["login"])]
            ).password = self.data_demo["password"]
            remote = self.env["res.remote"].search([("ip", "=", self.remote_addr)])
            if remote:
                remote.unlink()

        http.request = type(
            "obj",
            (object,),
            {
                "env": self.env,
                "cr": self.env.cr,
                "db": self.env.cr.dbname,
                "endpoint": type("obj", (object,), {"routing": []}),
                "httprequest": type(
                    "obj",
                    (object,),
                    {"remote_addr": self.remote_addr},
                ),
            },
        )

    def test_xmlrpc_login_ok(self, *args):
        """Test Login"""
        data1 = self.data_demo
        self.assertTrue(
            self.xmlrpc_common.authenticate(
                self.env.cr.dbname, data1["login"], data1["password"], {}
            )
        )
        with self.cursor() as cr:
            env = self.env(cr)
            self.assertTrue(env["res.remote"].search([("ip", "=", self.remote_addr)]))

    def test_xmlrpc_login_failure(self, *args):
        """Test Login Failure"""
        data1 = self.data_demo
        data1["password"] = "Failure!"
        self.assertFalse(
            self.xmlrpc_common.authenticate(
                self.env.cr.dbname, data1["login"], data1["password"], {}
            )
        )
        with self.cursor() as cr:
            env = self.env(cr)
            self.assertTrue(env["res.remote"].search([("ip", "=", self.remote_addr)]))
