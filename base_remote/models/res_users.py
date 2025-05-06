# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import SUPERUSER_ID, api, models
from odoo.exceptions import AccessDenied
from odoo.tools import config


class ResUsers(models.Model):
    _inherit = "res.users"

    @classmethod
    def _auth_check_remote(cls, login, method):
        """Force a method to raise an AccessDenied on falsey return."""
        with cls.pool.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            remote = env["res.users"].remote
            if not config["test_enable"]:
                remote.ensure_one()
        result = method()
        if not result:
            # Force exception to record auth failure
            raise AccessDenied()
        return result

    # Override all auth-related core methods
    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        return cls._auth_check_remote(
            login,
            lambda: super(ResUsers, cls)._login(db, login, password, user_agent_env),
        )

    @classmethod
    def authenticate(cls, db, login, password, user_agent_env):
        return cls._auth_check_remote(
            login,
            lambda: super(ResUsers, cls).authenticate(
                db, login, password, user_agent_env
            ),
        )
