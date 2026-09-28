# Copyright 2026 Ametras intelligence GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
import logging
from unittest.mock import patch

from odoo import http
from odoo.tests.common import HOST, HttpCase, tagged
from odoo.tools import config

from odoo.addons.proxy_trusted_hops.patch import post_load


@tagged("post_install", "-at_install")
class TestHttp(HttpCase):
    def test_login_logs_client_address(self):
        """A request passing two proxies is logged with the client address."""
        self.startPatcher(patch.object(http, "ProxyFix", http.ProxyFix))
        self.startPatcher(
            patch.dict(config.options, proxy_mode=True, proxy_trusted_hops="2")
        )
        post_load()
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.env.cr.dbname,
                "login": "admin",
                "password": "wrong password",
            },
        }
        with self.assertLogs("odoo.addons.base.models.res_users", logging.INFO) as logs:
            self.url_open(
                "/web/session/authenticate",
                data=json.dumps(payload),
                headers={
                    "Content-Type": "application/json",
                    "X-Forwarded-For": "6.6.6.6, 1.2.3.4, 10.0.0.1",
                    "X-Forwarded-Host": f"{HOST}:{config['http_port']}",
                },
            )
        self.assertTrue(
            any(
                "Login failed" in line and line.endswith("from 1.2.3.4")
                for line in logs.output
            ),
            logs.output,
        )
