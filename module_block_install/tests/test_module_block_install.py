# Copyright 2026 Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from odoo import http
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged
from odoo.tools import config

from .. import hooks
from ..models import ir_module_module
from .common import ModuleBlockInstallCommon


def _fake_request(remote_addr="192.0.2.1"):
    return SimpleNamespace(httprequest=SimpleNamespace(remote_addr=remote_addr))


@tagged("post_install", "-at_install")
class TestModuleBlockInstall(ModuleBlockInstallCommon, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_dummy_modules(cls.env)
        cls.Module = cls.env["ir.module.module"]

    def _in_request(self, remote_addr="192.0.2.1"):
        return patch.object(ir_module_module, "request", _fake_request(remote_addr))

    def _config(self, **values):
        return patch.object(ir_module_module, "_get_config", return_value=values)

    def _assert_blocked(self, records, method_name, operation_word):
        states = {rec: rec.state for rec in self.Module.search([])}
        with (
            self._in_request(),
            self.assertLogs(ir_module_module.__name__, "WARNING") as logs,
            self.assertRaisesRegex(UserError, operation_word),
        ):
            getattr(records, method_name)()
        block_lines = [line for line in logs.output if "BLOCK access" in line]
        self.assertEqual(len(block_lines), 1, logs.output)
        self.assertIn(f"BLOCK access to module.{method_name}", block_lines[0])
        self.assertIn(self.env.user.login, block_lines[0])
        self.assertIn("192.0.2.1", block_lines[0])
        # nothing changed
        for rec, state in states.items():
            self.assertEqual(rec.state, state, rec.name)

    def test_blocked_in_request(self):
        self._assert_blocked(self.mod_uninstalled, "button_install", "installed")
        self._assert_blocked(
            self.mod_uninstalled, "button_immediate_install", "installed"
        )
        self._assert_blocked(self.mod_installed, "button_upgrade", "upgraded")
        self._assert_blocked(self.mod_installed, "button_immediate_upgrade", "upgraded")
        self._assert_blocked(self.mod_installed, "button_uninstall", "uninstalled")
        self._assert_blocked(
            self.mod_installed, "button_immediate_uninstall", "uninstalled"
        )
        self._assert_blocked(
            self.mod_installed, "button_uninstall_wizard", "uninstalled"
        )
        self._assert_blocked(self.mod_installed, "module_uninstall", "uninstalled")

    def test_message_lists_modules(self):
        with (
            self._in_request(),
            self.assertLogs(ir_module_module.__name__, "WARNING"),
            self.assertRaises(UserError) as error,
        ):
            self.mod_uninstalled.button_install()
        self.assertIn(self.mod_uninstalled.name, str(error.exception))

    def test_apply_scheduled_upgrades_blocked(self):
        self.mod_uninstalled.button_install()
        self.assertEqual(self.mod_uninstalled.state, "to install")
        wizard = self.env["base.module.upgrade"].create({})
        with (
            self._in_request(),
            self.assertLogs(ir_module_module.__name__, "WARNING"),
            self.assertRaises(UserError) as error,
        ):
            wizard.upgrade_module()
        self.assertIn(self.mod_uninstalled.name, str(error.exception))

    def test_allowed_outside_request(self):
        self.mod_uninstalled.button_install()
        self.assertEqual(self.mod_uninstalled.state, "to install")
        self.mod_installed.button_uninstall()
        self.assertEqual(self.mod_installed.state, "to remove")

    def test_bundle_upgrade_installs_new_dependency(self):
        # update_list scans every addon on disk and is not what is tested here
        with patch.object(type(self.Module), "update_list", return_value=[0, 0]):
            self.mod_bundle.button_upgrade()
        self.assertEqual(self.mod_bundle.state, "to upgrade")
        self.assertEqual(self.mod_uninstalled.state, "to install")

    def test_disabled_by_config(self):
        for value in (False, "False", "0", "false"):
            with self._config(enabled=value), self._in_request():
                self.mod_uninstalled.button_install()
                self.assertEqual(self.mod_uninstalled.state, "to install")
                self.mod_uninstalled.state = "uninstalled"

    def test_enabled_by_config(self):
        with self._config(enabled="True"):
            self._assert_blocked(self.mod_uninstalled, "button_install", "installed")

    def test_allowed_ips(self):
        allowed = "203.0.113.10, 198.51.100.0/24,not-an-ip"
        with self._config(allowed_ips=allowed):
            for address in ("203.0.113.10", "198.51.100.25"):
                with (
                    self._in_request(address),
                    self.assertLogs(ir_module_module.__name__, "WARNING") as logs,
                ):
                    self.mod_uninstalled.button_install()
                self.assertIn("ignoring invalid allowed IP 'not-an-ip'", logs.output[0])
                self.assertEqual(self.mod_uninstalled.state, "to install")
                self.mod_uninstalled.state = "uninstalled"
            self._assert_blocked(self.mod_uninstalled, "button_install", "installed")
            # no remote address: blocked without even reading the allowed IPs
            with (
                self._in_request(None),
                self.assertLogs(ir_module_module.__name__, "WARNING"),
                self.assertRaises(UserError),
            ):
                self.mod_uninstalled.button_install()

    def test_config_file_section(self):
        tmp_dir = self.enterContext(tempfile.TemporaryDirectory())
        cfg_path = os.path.join(tmp_dir, "odoo.conf")
        with open(cfg_path, "w") as cfg:
            cfg.write(
                "[options]\n"
                "enabled = False\n"
                "[module_block_install]\n"
                "enabled = False\n"
                "allowed_ips = 203.0.113.10\n"
            )
        with (
            patch.dict(config.options, {"config": cfg_path}),
            patch.dict(sys.modules, {"odoo.addons.server_environment": None}),
        ):
            self.assertEqual(
                ir_module_module._get_config(),
                {"enabled": "False", "allowed_ips": "203.0.113.10"},
            )
            self.assertFalse(ir_module_module._is_blocking_enabled())
            with open(cfg_path, "w") as cfg:
                cfg.write("[options]\n")
            # no section: blocking on, nothing allowed
            self.assertEqual(ir_module_module._get_config(), {})
            self.assertTrue(ir_module_module._is_blocking_enabled())

    def test_borrowed_request_blocked(self):
        """``dispatch_rpc`` borrows the request: it is still an HTTP call."""
        self.assertTrue(getattr(http.borrow_request, "_module_block_install", False))
        fake = _fake_request()
        token = hooks.borrowed_request.set(fake)
        try:
            with patch.object(ir_module_module, "request", None):
                self.assertIs(ir_module_module._get_http_request(), fake)
                with (
                    self.assertLogs(ir_module_module.__name__, "WARNING"),
                    self.assertRaises(UserError),
                ):
                    self.mod_uninstalled.button_install()
        finally:
            hooks.borrowed_request.reset(token)
        self.assertEqual(self.mod_uninstalled.state, "uninstalled")

    def test_patch_borrow_request_idempotent(self):
        patched = http.borrow_request
        hooks._patch_borrow_request()
        self.assertIs(http.borrow_request, patched)
