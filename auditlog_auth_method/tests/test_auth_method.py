# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from types import SimpleNamespace
from unittest.mock import patch

from odoo import SUPERUSER_ID
from odoo.tests.common import TransactionCase, new_test_user

from ..rpc import RPC_CALL

CLASSIFIER_REQUEST = (
    "odoo.addons.auditlog_auth_method.models.auditlog_auth_method.request"
)
LOGIN_REQUEST = "odoo.addons.auditlog_auth_method.models.res_users.request"


class FakeSession(dict):
    def __init__(self, uid=None, **values):
        super().__init__(**values)
        self.uid = uid


class TestAuditlogAuthMethod(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.AuthMethod = cls.env["auditlog.auth.method"]
        cls.ResUsers = cls.env["res.users"]
        # Instances
        cls.password = "auditlog-auth-method-pwd"
        cls.user = new_test_user(
            cls.env, login="auditlog_auth_method_user", password=cls.password
        )
        cls.api_key = (
            cls.env["res.users.apikeys"].with_user(cls.user)._generate(None, "Test key")
        )
        # Existing instances
        cls.public_user = cls.env.ref("base.public_user")

    def setUp(self):
        super().setUp()
        self.addCleanup(self.registry.clear_cache)

    def _fake_request(self, session_uid=None, env_uid=None, route_auth=None, **values):
        return SimpleNamespace(
            session=FakeSession(uid=session_uid, **values),
            env=self.env(user=env_uid) if env_uid else None,
            _auditlog_route_auth=(route_auth, env_uid),
        )

    def _get_auth_info(self, fake_request=None):
        with patch(CLASSIFIER_REQUEST, fake_request):
            return self.AuthMethod._get_current_auth_info()

    def _get_rpc_auth_info(self, passwd, dbname=None):
        token = RPC_CALL.set((dbname or self.env.cr.dbname, self.user.id, passwd))
        try:
            return self.AuthMethod._get_current_auth_info()
        finally:
            RPC_CALL.reset(token)

    def test_server_without_request(self):
        self.assertEqual(self._get_auth_info(), ("server", None, None))

    def test_rpc_password(self):
        self.assertEqual(
            self._get_rpc_auth_info(self.password), ("rpc_password", None, None)
        )

    def test_rpc_api_key(self):
        for _attempt in range(2):
            self.assertEqual(
                self._get_rpc_auth_info(self.api_key),
                ("rpc_api_key", None, "Test key"),
            )

    def test_rpc_other_database(self):
        self.assertEqual(
            self._get_rpc_auth_info(self.api_key, dbname="other_database"),
            ("server", None, None),
        )

    def test_rpc_oauth(self):
        if "oauth_access_token" not in self.ResUsers._fields:
            self.skipTest("auth_oauth is not installed")
        self.env.cr.execute(
            "UPDATE res_users SET oauth_access_token = %s WHERE id = %s",
            ("oauth-token", self.user.id),
        )
        self.assertEqual(
            self._get_rpc_auth_info("oauth-token"), ("rpc_oauth", None, None)
        )

    def test_web_session_stamped(self):
        fake_request = self._fake_request(
            session_uid=self.user.id,
            env_uid=self.user.id,
            route_auth="user",
            auditlog_auth_method="web_password",
            auditlog_mfa_method="totp",
        )
        self.assertEqual(
            self._get_auth_info(fake_request), ("web_password", "totp", None)
        )

    def test_web_session_unknown(self):
        fake_request = self._fake_request(
            session_uid=self.user.id, env_uid=self.user.id, route_auth="user"
        )
        self.assertEqual(self._get_auth_info(fake_request), ("web_unknown", None, None))

    def test_web_superuser(self):
        fake_request = self._fake_request(
            session_uid=SUPERUSER_ID,
            env_uid=SUPERUSER_ID,
            route_auth="user",
            auditlog_auth_method="web_password",
            auditlog_mfa_method="none",
        )
        self.assertEqual(
            self._get_auth_info(fake_request), ("web_superuser", "none", None)
        )

    def test_public(self):
        fake_request = self._fake_request(
            env_uid=self.public_user.id, route_auth="public"
        )
        self.assertEqual(self._get_auth_info(fake_request), ("public", None, None))

    def test_public_custom_route_auth(self):
        fake_request = self._fake_request(
            env_uid=self.public_user.id, route_auth="calendar"
        )
        self.assertEqual(self._get_auth_info(fake_request), ("public", None, None))

    def test_route_token(self):
        fake_request = self._fake_request(env_uid=self.user.id, route_auth="outlook")
        self.assertEqual(self._get_auth_info(fake_request), ("route_token", None, None))

    def test_server_auth_none_route(self):
        fake_request = self._fake_request(env_uid=self.user.id, route_auth="none")
        self.assertEqual(self._get_auth_info(fake_request), ("server", None, None))

    def test_server_without_route_stash(self):
        fake_request = SimpleNamespace(session=FakeSession(), env=None)
        self.assertEqual(self._get_auth_info(fake_request), ("server", None, None))

    def test_login_stamps_session(self):
        self.registry.enter_test_mode(self.env.cr)
        self.addCleanup(self.registry.leave_test_mode)
        fake_request = SimpleNamespace(session=FakeSession())
        with patch(LOGIN_REQUEST, fake_request):
            self.ResUsers._login(
                self.env.cr.dbname,
                self.user.login,
                self.password,
                {"interactive": True},
            )
        self.assertEqual(fake_request.session["auditlog_auth_method"], "web_password")
        self.assertEqual(fake_request.session["auditlog_mfa_method"], "none")

    def test_login_non_interactive_not_stamped(self):
        self.registry.enter_test_mode(self.env.cr)
        self.addCleanup(self.registry.leave_test_mode)
        fake_request = SimpleNamespace(session=FakeSession())
        with patch(LOGIN_REQUEST, fake_request):
            self.ResUsers._login(
                self.env.cr.dbname,
                self.user.login,
                self.password,
                {"interactive": False},
            )
        self.assertFalse(fake_request.session)

    def test_mfa_method(self):
        users_class = type(self.ResUsers)
        for mfa_type, expected in (
            (None, "none"),
            ("totp", "totp"),
            ("totp_mail", "totp_mail"),
            ("custom", "other"),
        ):
            with patch.object(users_class, "_mfa_type", return_value=mfa_type):
                self.assertEqual(self.user._auditlog_get_mfa_method(), expected)
