# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import json
import xmlrpc

from odoo.tests import common


@common.tagged("post_install", "-at_install")
class TestXMLRPC(common.HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_uid = cls.env.ref("base.user_admin").id

    def _set_disable(self, val):
        type(self.env["res.partner"])._disable_rpc = val

    def _set_disable_on_model(self, val):
        self.env["ir.model"]._get("res.partner").rpc_config_edit = json.dumps(
            {"disable": val}
        )
        self.env.flush_all()

    def tearDown(self):
        klass = type(self.env["res.partner"])
        if hasattr(klass, "_disable_rpc"):
            delattr(klass, "_disable_rpc")
        super().tearDown()

    def _rpc_call(self, method, vals=None):
        o = self.xmlrpc_object
        db_name = common.get_db_name()
        return o.execute(
            db_name, self.admin_uid, "admin", "res.partner", method, vals or []
        )

    def test_xmlrpc_search_normal(self):
        res = self._rpc_call("search")
        self.assertTrue(isinstance(res, list))

    def test_xmlrpc_all_blocked(self):
        self._set_disable(("all",))
        msg = "RPC call on res.partner is not allowed"
        with self.assertRaisesRegex(xmlrpc.client.Fault, msg):
            self._rpc_call("search")

        with self.assertRaisesRegex(xmlrpc.client.Fault, msg):
            self._rpc_call("create", vals=[{"name": "Foo"}])

    def test_xmlrpc_can_search_create_blocked(self):
        self._set_disable(("create",))
        self._rpc_call("search")

        msg = "RPC call on res.partner is not allowed"
        with self.assertRaisesRegex(xmlrpc.client.Fault, msg):
            self._rpc_call("create", vals=[{"name": "Foo"}])

    def test_xmlrpc_all_blocked__ir_model(self):
        self._set_disable_on_model(("all",))
        msg = "RPC call on res.partner is not allowed"
        with self.assertRaisesRegex(xmlrpc.client.Fault, msg):
            self._rpc_call("search")

        with self.assertRaisesRegex(xmlrpc.client.Fault, msg):
            self._rpc_call("create", vals=[{"name": "Foo"}])

    def test_xmlrpc_can_search_create_blocked__ir_model(self):
        self._set_disable_on_model(("create",))
        self._rpc_call("search")

        msg = "RPC call on res.partner is not allowed"
        with self.assertRaisesRegex(xmlrpc.client.Fault, msg):
            self._rpc_call("create", vals=[{"name": "Foo"}])
