# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import tests
from odoo.api import Environment

from odoo.addons.base_contextvars.contextvars_patch import _odoo_environments_ctx


class TestContextvars(tests.common.TransactionCase):
    def test_contextvars(self):
        envs = Environment.envs
        self.assertTrue(envs)
        self.assertTrue(
            _odoo_environments_ctx.get() is envs
            or getattr(Environment._local, "environments", ()) is envs
        )
        with Environment.manage():
            self.assertTrue(_odoo_environments_ctx.get() is envs)
