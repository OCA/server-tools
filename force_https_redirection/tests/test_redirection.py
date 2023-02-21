import odoo.tools
from odoo.tests import common, tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
class TestRedirectionBehindReverseProxy(HttpCase):
    """Testing various scenario with and without proxy

    In case of reverse proxy we expect the HTTP_X_FORWARDED_PROTO
    header set with the protocol used between client and the reverse proxy

    * Case when an http request initiate by the client::

        client <--HTTP--> reverse proxy <--HTTP--> odoo

        HTTP_X_FORWARDED_PROTO is set to `http` we should redirect

    * Case when an https request initiate by the client:

        client <--HTTPS--> reverse proxy <--HTTP--> odoo

        HTTP_X_FORWARDED_PROTO is set to `https` we should not redirect

    * in case of no reverse proxy (likes wkhtml2pdf in some configuration ?!)

        client <--HTTP--> odoo

        HTTP_X_FORWARDED_PROTO is not set `https` shouldn't redirect

    To make those test passed you needs to set following options in odoo.cfg::

        force_https_redirection=true
        server_wide_modules=base,web,force_https_redirection

    """

    def setUp(self):
        super().setUp()
        self.domain_port = "%s:%s" % (common.HOST, odoo.tools.config["http_port"])

    def test_http_with_proxy_should_redirect(self):
        res = self.url_open(
            "/", allow_redirects=False, headers={"X-FORWARDED-PROTO": "http"}
        )
        self.assertEqual(
            res.status_code,
            301,
            f"got {res.status_code} to {res._next.url if res._next else None}",
        )
        self.assertEqual(
            res._next.url,
            f"https://{self.domain_port}/",
        )

    def test_http_without_proxy_should_not_redirect_to_https(self):
        res = self.url_open("/", allow_redirects=False, headers={})
        self.assertEqual(
            res.status_code,
            303,
            f"got {res.status_code} to {res._next.url if res._next else None}",
        )
        self.assertEqual(
            res._next.url,
            f"http://{self.domain_port}/web",
        )

    def test_https_with_proxy_should_not_redirect(self):
        res = self.url_open(
            "/", allow_redirects=False, headers={"X-FORWARDED-PROTO": "https"}
        )
        self.assertEqual(
            res.status_code,
            303,
            f"got {res.status_code} to {res._next.url if res._next else None}",
        )
        # we assume we are in https that fine to get the 303
        # and the http:// as we are not realy using https in this test
        # the purpose is to avoid infinite loop
        self.assertEqual(
            res._next.url,
            f"http://{self.domain_port}/web",
        )

    def test_404_should_first_redirect_to_https_that_contains_http(self):
        res = self.url_open(
            "/unknown-http-path",
            allow_redirects=False,
            headers={"X-FORWARDED-PROTO": "http"},
        )
        self.assertEqual(res.status_code, 301)
        self.assertEqual(
            res._next.url,
            f"https://{self.domain_port}/unknown-http-path",
        )


@common.tagged("post_install", "-at_install")
class TestJSONRPC(common.HttpCase):
    def setUp(self):
        super().setUp()
        self.admin_uid = self.env.ref("base.user_admin").id
        self.db_name = common.get_db_name()
        self.uid = self.xmlrpc_common.login(self.db_name, "admin", "admin")
        self.json_rpc_url = "http://%s:%s/jsonrpc" % (
            common.HOST,
            odoo.tools.config["http_port"],
        )

    def _json_call(self, *args, headers=None):
        return self.opener.post(
            self.json_rpc_url,
            json={
                "jsonrpc": "2.0",
                "id": None,
                "method": "call",
                "params": {"service": "object", "method": "execute", "args": args},
            },
            allow_redirects=False,
            headers=headers,
        )

    def test_http_with_proxy_should_redirect(self):
        res = self._json_call(
            self.db_name,
            self.admin_uid,
            "admin",
            "res.partner",
            "name_search",
            "admin",
            headers={"X-FORWARDED-PROTO": "http"},
        )
        self.assertEqual(
            res.status_code,
            301,
        )
        self.assertEqual(
            res._next.url,
            self.json_rpc_url.replace("http", "https", 1),
        )

    def test_http_without_proxy_should_not_redirect_to_https(self):
        res = self._json_call(
            self.db_name,
            self.admin_uid,
            "admin",
            "res.partner",
            "name_search",
            "admin",
        )
        self.assertEqual(
            res.status_code,
            200,
            f"got {res.status_code} to {res._next.url if res._next else None}",
        )

    def test_https_with_proxy_should_not_redirect(self):
        res = self._json_call(
            self.db_name,
            self.admin_uid,
            "admin",
            "res.partner",
            "name_search",
            "admin",
            headers={"X-FORWARDED-PROTO": "https"},
        )
        self.assertEqual(
            res.status_code,
            200,
            f"got {res.status_code} to {res._next.url if res._next else None}",
        )
