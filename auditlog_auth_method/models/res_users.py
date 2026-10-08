# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api, models, tools
from odoo.http import request

from odoo.addons.base.models.res_users import INDEX_SIZE, KEY_CRYPT_CONTEXT

from .auditlog_log import MFA_METHODS


class ResUsers(models.Model):
    _inherit = "res.users"

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        uid = super()._login(db, login, password, user_agent_env=user_agent_env)
        if request and user_agent_env and user_agent_env.get("interactive"):
            with cls.pool.cursor() as cr:
                user = api.Environment(cr, SUPERUSER_ID, {})[cls._name].browse(uid)
                request.session[
                    "auditlog_auth_method"
                ] = user._auditlog_get_login_auth_method(password)
                request.session["auditlog_mfa_method"] = user._auditlog_get_mfa_method()
        return uid

    def _auditlog_get_login_auth_method(self, password):
        self.ensure_one()
        if self._auditlog_is_oauth_access_token(password):
            return "web_oauth"
        return "web_password"

    def _auditlog_get_mfa_method(self):
        self.ensure_one()
        mfa_method = self._mfa_type() or "none"
        if mfa_method not in dict(MFA_METHODS):
            return "other"
        return mfa_method

    def _auditlog_is_oauth_access_token(self, token):
        self.ensure_one()
        if "oauth_access_token" not in self._fields:
            return False
        self.env.cr.execute(
            "SELECT 1 FROM res_users WHERE id = %s AND oauth_access_token = %s",
            (self.id, token),
        )
        return bool(self.env.cr.fetchone())

    @api.model
    @tools.ormcache("uid", "passwd")
    def _auditlog_get_rpc_credential(self, uid, passwd):
        self.env.cr.execute(
            """
            SELECT name, key
            FROM res_users_apikeys
            WHERE user_id = %s
                AND index = %s
                AND (scope IS NULL OR scope = 'rpc')
            """,
            (uid, passwd[:INDEX_SIZE]),
        )
        for name, key in self.env.cr.fetchall():
            if KEY_CRYPT_CONTEXT.verify(passwd, key):
                return "rpc_api_key", name
        if self.browse(uid)._auditlog_is_oauth_access_token(passwd):
            return "rpc_oauth", None
        return "rpc_password", None
