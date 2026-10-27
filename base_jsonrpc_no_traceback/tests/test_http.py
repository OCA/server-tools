# Copyright 2026 Akretion France (https://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from unittest.mock import patch

from odoo.tests import HttpCase, tagged
from odoo.tools import config, mute_logger


@tagged("post_install", "-at_install")
class TestJsonRpcNoTraceback(HttpCase):
    def _call(self, query_string=""):
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "this_method_does_not_exist",
                "args": [],
            },
            "id": 0,
        }
        # The request intentionally raises an error, which would otherwise be
        # logged by odoo.http and rejected by checklog-odoo in the CI.
        with mute_logger("odoo.http"):
            return self.url_open(
                "/jsonrpc" + query_string,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )

    def test_anonymous_debug_query_string_has_no_traceback(self):
        with patch.dict(config.options, {"dev_mode": []}):
            response = self._call("?debug=1")
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["data"]["debug"], "")

    def test_traceback_in_dev_mode(self):
        with patch.dict(config.options, {"dev_mode": ["all"]}):
            response = self._call()
        data = response.json()
        self.assertIn(
            "Traceback (most recent call last)", data["error"]["data"]["debug"]
        )
