# Copyright 2026 Ametras intelligence GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os
from unittest.mock import patch

from odoo import http
from odoo.tests.common import BaseCase
from odoo.tools import config

from odoo.addons.proxy_trusted_hops.patch import _get_trusted_hops, post_load

FORWARDED_FOR = "6.6.6.6, 1.2.3.4, 10.0.0.1"


class TestPatch(BaseCase):
    def setUp(self):
        super().setUp()
        # Restore the core ProxyFix after each test.
        self.startPatcher(patch.object(http, "ProxyFix", http.ProxyFix))
        self.startPatcher(patch.dict(os.environ))
        os.environ.pop("ODOO_PROXY_TRUSTED_HOPS", None)

    def _set_option(self, value):
        self.startPatcher(patch.dict(config.options, proxy_trusted_hops=value))

    def _remote_addr(self):
        environ = {
            "REMOTE_ADDR": "10.0.0.2",
            "HTTP_HOST": "internal:8069",
            "HTTP_X_FORWARDED_FOR": FORWARDED_FOR,
            "HTTP_X_FORWARDED_HOST": "odoo.example.com",
            "wsgi.url_scheme": "http",
        }
        http.ProxyFix(lambda env, start_response: [])(environ, lambda *args: None)
        return environ["REMOTE_ADDR"]

    def test_default_keeps_core_behavior(self):
        self._set_option(None)
        self.assertEqual(_get_trusted_hops(), 1)
        post_load()
        self.assertEqual(self._remote_addr(), "10.0.0.1")

    def test_config_option(self):
        self._set_option("2")
        self.assertEqual(_get_trusted_hops(), 2)
        post_load()
        self.assertEqual(self._remote_addr(), "1.2.3.4")

    def test_environment_variable(self):
        self._set_option(None)
        os.environ["ODOO_PROXY_TRUSTED_HOPS"] = "3"
        self.assertEqual(_get_trusted_hops(), 3)
        post_load()
        self.assertEqual(self._remote_addr(), "6.6.6.6")

    def test_config_option_wins_over_environment_variable(self):
        self._set_option("2")
        os.environ["ODOO_PROXY_TRUSTED_HOPS"] = "3"
        self.assertEqual(_get_trusted_hops(), 2)

    def test_fewer_entries_than_hops_keeps_peer_address(self):
        self._set_option("4")
        post_load()
        self.assertEqual(self._remote_addr(), "10.0.0.2")

    def test_invalid_value_falls_back_to_core_behavior(self):
        for value in ("0", "-1", "two"):
            with self.subTest(value=value):
                self._set_option(value)
                with self.assertLogs("odoo.addons.proxy_trusted_hops.patch", "ERROR"):
                    self.assertEqual(_get_trusted_hops(), 1)
