# Copyright 2026 Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import xmlrpc.client

from odoo.tests import HttpCase, tagged
from odoo.tests.common import JsonRpcException
from odoo.tools import mute_logger

from .common import ModuleBlockInstallCommon

_MODELS_LOGGER = "odoo.addons.module_block_install.models.ir_module_module"


@tagged("post_install", "-at_install")
class TestModuleBlockInstallHttp(ModuleBlockInstallCommon, HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_dummy_modules(cls.env)

    @mute_logger("odoo.http")
    def test_immediate_install_over_jsonrpc(self):
        self.authenticate("admin", "admin")
        with (
            self.assertLogs(_MODELS_LOGGER, "WARNING"),
            self.assertRaises(JsonRpcException) as error,
        ):
            self.make_jsonrpc_request(
                "/web/dataset/call_kw/ir.module.module/button_immediate_install",
                {
                    "model": "ir.module.module",
                    "method": "button_immediate_install",
                    "args": [self.mod_uninstalled.ids],
                    "kwargs": {},
                },
            )
        self.assertEqual(error.exception.args[0], "odoo.exceptions.UserError")
        self.assertEqual(self.mod_uninstalled.state, "uninstalled")

    # /xmlrpc/2 and /jsonrpc run the call inside ``borrow_request()``, which
    # unbinds ``odoo.http.request``: they must be blocked all the same.

    @mute_logger("odoo.http", "odoo.addons.rpc.controllers.xmlrpc")
    def test_immediate_install_over_xmlrpc(self):
        with (
            self.assertLogs(_MODELS_LOGGER, "WARNING") as logs,
            self.assertRaises(xmlrpc.client.Fault) as error,
        ):
            self.xmlrpc_object.execute_kw(
                self.env.cr.dbname,
                self.env.ref("base.user_admin").id,
                "admin",
                "ir.module.module",
                "button_immediate_install",
                [self.mod_uninstalled.ids],
            )
        self.assertIn("Module installation is disabled", error.exception.faultString)
        self.assertIn("127.0.0.1", logs.output[0])
        self.assertEqual(self.mod_uninstalled.state, "uninstalled")

    @mute_logger("odoo.http", "odoo.addons.rpc.controllers.jsonrpc")
    def test_immediate_install_over_legacy_jsonrpc(self):
        with (
            self.assertLogs(_MODELS_LOGGER, "WARNING"),
            self.assertRaises(JsonRpcException) as error,
        ):
            self.make_jsonrpc_request(
                "/jsonrpc",
                {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        self.env.cr.dbname,
                        self.env.ref("base.user_admin").id,
                        "admin",
                        "ir.module.module",
                        "button_immediate_install",
                        [self.mod_uninstalled.ids],
                    ],
                },
            )
        self.assertEqual(error.exception.args[0], "odoo.exceptions.UserError")
        self.assertEqual(self.mod_uninstalled.state, "uninstalled")
