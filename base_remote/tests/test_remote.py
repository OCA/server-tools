# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import socket
from unittest.mock import patch

from odoo import http
from odoo.exceptions import AccessDenied
from odoo.tests import tagged
from odoo.tests.common import TEST_CURSOR_COOKIE_NAME, HttpCase
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
# Skip CSRF validation on tests
@patch(http.__name__ + ".Request.validate_csrf", return_value=True)
class TestRemote(HttpCase):
    def setUp(self):
        super().setUp()

        # Complex password to avoid conflicts with `password_security`
        self.good_password = "Admin$%02584"
        self.data_user = {
            "login": "base_remote_test",
            "password": "Demo%&/(908409**",
        }
        self.remote_addr = "127.0.0.1"
        with self.cursor() as cr:
            env = self.env(cr)
            # Make sure involved users have good passwords
            env.user.password = self.good_password
            user = env["res.users"].search([("login", "=", self.data_user["login"])])
            if user:
                user.password = self.data_user["password"]
            else:
                env["res.users"].create(
                    {
                        "name": "Base Remote Test",
                        "login": self.data_user["login"],
                        "password": self.data_user["password"],
                        "group_ids": [(6, 0, [env.ref("base.group_user").id])],
                    }
                )
            remote = self.env["res.remote"].search([("ip", "=", self.remote_addr)])
            if remote:
                remote.unlink()

        self.original_request = http.request
        http.request = type(
            "obj",
            (object,),
            {
                "env": self.env,
                "cr": self.env.cr,
                "db": self.env.cr.dbname,
                "cookies": {TEST_CURSOR_COOKIE_NAME: self.http_request_key},
                "endpoint": type("obj", (object,), {"routing": []}),
                "httprequest": type(
                    "obj",
                    (object,),
                    {
                        "remote_addr": self.remote_addr,
                        "cookies": {},
                        "path": "/xmlrpc/2/common",
                    },
                ),
            },
        )

    def tearDown(self):
        super().tearDown()
        http.request = self.original_request

    @mute_logger("odoo.addons.rpc.controllers.xmlrpc")
    def test_xmlrpc_login_ok(self, *args):
        """Test Login"""
        data1 = self.data_user
        self.assertTrue(
            self.xmlrpc_common.authenticate(
                self.env.cr.dbname, data1["login"], data1["password"], {}
            )
        )
        with self.cursor() as cr:
            env = self.env(cr)
            self.assertTrue(env["res.remote"].search([("ip", "=", self.remote_addr)]))

    @mute_logger("odoo.addons.rpc.controllers.xmlrpc")
    def test_xmlrpc_login_failure(self, *args):
        """Test Login Failure"""
        data1 = self.data_user
        data1["password"] = "Failure!"
        self.assertFalse(
            self.xmlrpc_common.authenticate(
                self.env.cr.dbname, data1["login"], data1["password"], {}
            )
        )
        with self.cursor() as cr:
            env = self.env(cr)
            self.assertTrue(env["res.remote"].search([("ip", "=", self.remote_addr)]))

    def test_remote_without_request(self, *args):
        with patch.object(http, "request", None):
            self.assertFalse(self.env["res.users"].remote)

    @mute_logger("odoo.addons.base_remote.models.res_remote")
    def test_get_remote_hostname_not_found(self, *args):
        addr = "203.0.113.1"
        with patch(
            "odoo.addons.base_remote.models.res_remote.socket.gethostbyaddr",
            side_effect=socket.herror,
        ):
            remote = self.env["res.remote"]._get_remote(addr)
        self.assertEqual(remote.name, addr)
        self.assertFalse(remote.in_network)

    def test_get_remote_ip_updated(self, *args):
        self.env["res.remote"].create(
            {"name": "known.host", "ip": "203.0.113.2", "in_network": True}
        )
        with patch(
            "odoo.addons.base_remote.models.res_remote.socket.gethostbyaddr",
            return_value=("known.host", [], ["203.0.113.3"]),
        ):
            remote = self.env["res.remote"]._get_remote("203.0.113.3")
        self.assertEqual(remote.name, "known.host")
        self.assertEqual(remote.ip, "203.0.113.3")

    def test_auth_check_remote_denied(self, *args):
        with self.assertRaises(AccessDenied):
            self.env["res.users"]._auth_check_remote({}, lambda: False)
