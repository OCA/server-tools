# Copyright 2026 Ametras intelligence GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import json
import logging
import os
import sys
import tempfile
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
        self.startPatcher(patch.dict(os.environ))
        os.environ.pop("ODOO_TRUSTED_PROXIES", None)
        handle, path = tempfile.mkstemp(suffix=".conf")
        with os.fdopen(handle, "w") as config_file:
            config_file.write("[proxy_trusted_hops]\ntrusted_proxies = 2\n")
        self.addCleanup(os.remove, path)
        self.startPatcher(patch.object(config, "rcfile", path))
        self.startPatcher(patch.dict(config.options, proxy_mode=True))
        # Only while reading the configuration: restoring sys.modules after the
        # request would drop the modules it imported.
        with patch.dict(sys.modules, {"odoo.addons.server_environment": None}):
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
