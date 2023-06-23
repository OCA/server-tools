# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http, tests


class FutureResponseTestController(http.Controller):
    @http.route("/test_future_response", type="http", auth="public")
    def test_future_response(self):
        http.request.future_response.headers["x-test-future-response"] = "test"
        return http.request.make_response("ok", headers={"x-test-response": "test"})


class TestFutureResponse(tests.HttpCase):
    def test_future_response(self):
        resp = self.url_open("/test_future_response")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text, "ok")
        self.assertEqual(resp.headers["x-test-future-response"], "test")
        self.assertEqual(resp.headers["x-test-response"], "test")
