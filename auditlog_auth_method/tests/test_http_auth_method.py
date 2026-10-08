# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, get_db_name, new_test_user, tagged

from odoo.addons.auditlog.tests.common import AuditLogRuleCommon


@tagged("post_install", "-at_install")
class TestAuditlogAuthMethodHttp(AuditLogRuleCommon, HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.Log = cls.env["auditlog.log"]
        # Instances
        cls.password = "auditlog-auth-method-pwd"
        cls.user = new_test_user(
            cls.env,
            login="auditlog_auth_http_user",
            password=cls.password,
            groups="base.group_user,base.group_partner_manager",
        )
        cls.admin_user = new_test_user(
            cls.env,
            login="auditlog_auth_http_admin",
            password=cls.password,
            groups="base.group_user,base.group_system",
        )
        cls.api_key = (
            cls.env["res.users.apikeys"]
            .with_user(cls.user)
            ._generate(None, "Integration key")
        )
        cls.rule = cls.create_rule(
            {
                "name": "Auth method HTTP rule",
                "model_id": cls.env.ref("base.model_res_partner_category").id,
                "log_create": True,
                "log_type": "full",
            }
        )
        cls.rule.subscribe()
        # Existing instances
        cls.api_key_method = cls.env.ref("auditlog_auth_method.auth_method_rpc_api_key")

    def setUp(self):
        super().setUp()
        self.addCleanup(self.registry.clear_cache)

    def _rpc_create(self, password, vals):
        if isinstance(vals, str):
            vals = {"name": vals}
        return self.xmlrpc_object.execute_kw(
            get_db_name(),
            self.user.id,
            password,
            "res.partner.category",
            "create",
            [vals],
        )

    def _web_login(self, user):
        self.make_jsonrpc_request(
            "/web/session/authenticate",
            {"db": get_db_name(), "login": user.login, "password": self.password},
        )

    def _web_create(self, name):
        return self.make_jsonrpc_request(
            "/web/dataset/call_kw/res.partner.category/create",
            {
                "model": "res.partner.category",
                "method": "create",
                "args": [{"name": name}],
                "kwargs": {},
            },
        )

    def _get_log(self, res_id):
        return self.Log.search(
            [
                ("model_id", "=", self.rule.model_id.id),
                ("res_id", "in", res_id if isinstance(res_id, list) else [res_id]),
                ("method", "=", "create"),
            ]
        )

    def test_rpc_password(self):
        log = self._get_log(self._rpc_create(self.password, "RPC password"))
        self.assertEqual(log.auth_method_id.code, "rpc_password")
        self.assertEqual(log.user_id, self.user)
        self.assertFalse(log.auth_api_key_name)

    def test_rpc_http_request(self):
        res_ids = self._rpc_create(
            self.api_key, [{"name": "RPC request 1"}, {"name": "RPC request 2"}]
        )
        logs = self._get_log(res_ids)
        http_request = logs.http_request_id
        self.assertEqual(len(logs), 2)
        self.assertEqual(len(http_request), 1)
        self.assertEqual(http_request.name, "/xmlrpc/2/object")
        self.assertEqual(http_request.user_id, self.user)
        self.assertEqual(http_request.remote_addr, "127.0.0.1")
        self.assertIn("xmlrpc", http_request.user_agent.lower())
        self.assertFalse(logs.http_session_id)
        other_log = self._get_log(self._rpc_create(self.api_key, "RPC request 3"))
        self.assertNotEqual(other_log.http_request_id, http_request)

    def test_rpc_api_key(self):
        for name in ("RPC API key", "RPC API key cached"):
            log = self._get_log(self._rpc_create(self.api_key, name))
            self.assertEqual(log.auth_method_id.code, "rpc_api_key")
            self.assertEqual(log.auth_api_key_name, "Integration key")
            self.assertEqual(log.user_id, self.user)

    def test_web_password(self):
        self._web_login(self.user)
        log = self._get_log(self._web_create("Web password"))
        self.assertEqual(log.auth_method_id.code, "web_password")
        self.assertEqual(log.auth_mfa_method, "none")
        self.assertEqual(log.http_request_remote_addr, "127.0.0.1")
        self.assertTrue(log.http_request_user_agent)

    def test_web_unknown(self):
        self.authenticate(self.user.login, self.password)
        log = self._get_log(self._web_create("Web unknown"))
        self.assertEqual(log.auth_method_id.code, "web_unknown")

    def test_web_superuser(self):
        self._web_login(self.admin_user)
        self.url_open("/web/become", allow_redirects=False)
        log = self._get_log(self._web_create("Web superuser"))
        self.assertEqual(log.auth_method_id.code, "web_superuser")

    def test_rule_filter(self):
        self.rule.auth_method_ids = self.api_key_method
        password_id = self._rpc_create(self.password, "Filtered out")
        api_key_id = self._rpc_create(self.api_key, "Filtered in")
        self._web_login(self.user)
        web_id = self._web_create("Web filtered out")
        self.assertFalse(self._get_log(password_id))
        self.assertFalse(self._get_log(web_id))
        self.assertTrue(self._get_log(api_key_id))
