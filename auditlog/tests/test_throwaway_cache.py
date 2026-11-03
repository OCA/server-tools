# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon

from ..models.auditlog_rule import ThrowAwayCache


class TestThrowAwayCache(BaseCommon):
    def test_env_first_used_inside_is_flushed_after(self):
        """An environment first used inside the throwaway cache must write to
        the real transaction once the context manager is left."""
        partner = self.env["res.partner"].create({"name": "Before"})
        self.env.flush_all()
        other = partner.sudo().with_context(auditlog_test_new_env=True)
        with ThrowAwayCache(self.env):
            # a query that flushes its fields binds the environment's
            # dirty-field registry
            self.assertEqual(other.search_count([("name", "=", "Before")]), 1)
        other.name = "After"
        self.env.flush_all()
        self.env.cr.execute("SELECT name FROM res_partner WHERE id = %s", [partner.id])
        self.assertEqual(self.env.cr.fetchone()[0], "After")
