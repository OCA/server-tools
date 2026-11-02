# Copyright 2026 Ametras intelligence GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import configparser
import os
import sys
import tempfile
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
        os.environ.pop("ODOO_TRUSTED_PROXIES", None)
        # Read the configuration file, even where server_environment is
        # available.
        self.startPatcher(
            patch.dict(sys.modules, {"odoo.addons.server_environment": None})
        )

    def _write_config(self, content):
        handle, path = tempfile.mkstemp(suffix=".conf")
        with os.fdopen(handle, "w") as config_file:
            config_file.write(content)
        self.addCleanup(os.remove, path)
        self.startPatcher(patch.object(config, "rcfile", path))

    def _set_option(self, value):
        content = "[options]\n"
        if value is not None:
            content += f"\n[proxy_trusted_hops]\ntrusted_proxies = {value}\n"
        self._write_config(content)

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

    def test_option_in_options_section_is_ignored(self):
        self._write_config("[options]\ntrusted_proxies = 2\n")
        self.assertEqual(_get_trusted_hops(), 1)

    def test_without_config_file(self):
        self.startPatcher(patch.object(config, "rcfile", None))
        self.assertEqual(_get_trusted_hops(), 1)

    def test_server_environment(self):
        serv_config = configparser.ConfigParser()
        serv_config.read_string("[proxy_trusted_hops]\ntrusted_proxies = 3\n")
        server_environment = type(sys)("odoo.addons.server_environment")
        server_environment.serv_config = serv_config
        sys.modules["odoo.addons.server_environment"] = server_environment
        self._set_option("2")
        self.assertEqual(_get_trusted_hops(), 3)
        serv_config.remove_section("proxy_trusted_hops")
        self.assertEqual(_get_trusted_hops(), 1)

    def test_server_environment_option_name_ignores_case(self):
        # server_environment keeps the case of option names, ConfigParser
        # lowercases them: both must find the option.
        serv_config = configparser.ConfigParser()
        serv_config.optionxform = str
        serv_config.read_string("[proxy_trusted_hops]\nTrusted_Proxies = 3\n")
        server_environment = type(sys)("odoo.addons.server_environment")
        server_environment.serv_config = serv_config
        sys.modules["odoo.addons.server_environment"] = server_environment
        self.assertEqual(_get_trusted_hops(), 3)

    def test_environment_variable(self):
        self._set_option(None)
        os.environ["ODOO_TRUSTED_PROXIES"] = "3"
        self.assertEqual(_get_trusted_hops(), 3)
        post_load()
        self.assertEqual(self._remote_addr(), "6.6.6.6")

    def test_environment_variable_wins_over_config_option(self):
        self._set_option("2")
        os.environ["ODOO_TRUSTED_PROXIES"] = "3"
        self.assertEqual(_get_trusted_hops(), 3)

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
