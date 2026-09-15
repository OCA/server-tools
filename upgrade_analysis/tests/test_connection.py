from http.cookiejar import Cookie, CookieJar
from unittest import mock, skipIf
from urllib.request import HTTPCookieProcessor, build_opener

import odoorpc

from odoo.release import version
from odoo.tests.common import HOST, TEST_CURSOR_COOKIE_NAME, HttpCase, tagged
from odoo.tests.form import Form
from odoo.tools import mute_logger


class OdooTestCursorCookieHandler(HTTPCookieProcessor):
    def __init__(self, odoo_test_case):
        self.odoo_test_case = odoo_test_case
        super().__init__(CookieJar())

    def http_request(self, req):
        cookie_value = self.odoo_test_case.http_request_key
        self.cookiejar.set_cookie(
            Cookie(
                version=0,
                name=TEST_CURSOR_COOKIE_NAME,
                value=cookie_value,
                port=None,
                domain=HOST,
                path="/",
                domain_specified=None,
                domain_initial_dot=None,
                path_specified=None,
                secure=None,
                expires=None,
                discard=None,
                comment=None,
                comment_url=None,
                rest=None,
                rfc2109=None,
                port_specified=None,
            )
        )
        return super().http_request(req)


@tagged("-at_install", "post_install")
class TestConnection(HttpCase):
    def setUp(self):
        super().setUp()

        opener = build_opener(OdooTestCursorCookieHandler(self))
        self.http_request_key = self.canonical_tag

        original_init = odoorpc.ODOO.__init__

        def patched_init(ODOO_self, *args, **kwargs):
            return original_init(ODOO_self, *args, **dict(kwargs, opener=opener))

        self.startPatcher(mock.patch("odoorpc.ODOO.__init__", patched_init))

    @skipIf(
        odoorpc.__version__ <= "0.10.1",
        "Not testing API key functionality of odoorpc for versions <= 0.10.1",
    )
    def test_connection_api_key(self):
        """
        Test that connection via api key works
        """
        api_key = (
            self.env["res.users.apikeys"]
            .with_user(self.env.ref("base.user_admin"))
            ._generate("rpc", "upgrade_analysis", None)
        )
        with Form(self.env["upgrade.comparison.config"]) as form:
            form.server = HOST
            form.port = self.http_port()
            form.database = self.env.cr.dbname
            form.username = None
            form.password = None
            form.api_key = api_key
            config = form.save()

        with self.allow_requests():
            config.test_connection()
        self.assertEqual(config.version, version)

    def test_connection_login(self):
        """
        Test that connection via login works. Remove in v22
        """
        with Form(self.env["upgrade.comparison.config"]) as form:
            form.server = HOST
            form.port = self.http_port()
            form.database = self.env.cr.dbname
            config = form.save()

        with self.allow_requests(), mute_logger("odoo.addons.rpc.controllers.jsonrpc"):
            config.test_connection()
        self.assertEqual(config.version, version)
