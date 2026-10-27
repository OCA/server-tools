# Copyright 2026 360ERP (<https://www.360erp.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.tools import SQL

from ..models.auditlog_rule import ThrowAwayCache


class TestThrowAwayCache(common.TransactionCase):
    """The transaction is left intact by a ``ThrowAwayCache``.

    Environments keep the containers of the transaction they first see in
    cached properties (``env._protected``, ``env._field_dirty``), and are
    reused for the same user and context. The tests that create an environment
    within the ``ThrowAwayCache`` use a context key of their own, so that this
    environment is a new one.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.industry = cls.env["res.partner.industry"].create(
            {"name": "Throwaway", "full_name": "Throwaway cache"}
        )
        cls.env.flush_all()

    def test_protected_fields_are_restored(self):
        """The fields protected by an ongoing create/write stay protected."""
        field = self.industry._fields["full_name"]
        with self.env.protecting([field], self.industry):
            with ThrowAwayCache(self.env):
                self.assertFalse(self.env.is_protected(field, self.industry))
            self.assertTrue(self.env.is_protected(field, self.industry))

    def test_updates_of_an_env_first_used_inside_are_flushed(self):
        with ThrowAwayCache(self.env):
            industry = self.industry.with_context(test_throwaway_dirty=True)
            # Reading flushes first, which uses env._field_dirty
            self.assertTrue(industry.active)

        industry.write({"active": False})
        self.env.flush_all()

        self.assertEqual(
            self.env.execute_query(
                SQL(
                    "SELECT active FROM res_partner_industry WHERE id = %s",
                    self.industry.id,
                )
            ),
            [(False,)],
        )

    def test_env_first_used_inside_sees_protected_fields(self):
        with ThrowAwayCache(self.env):
            industry = self.industry.with_context(test_throwaway_protected=True)
            # A non-stored computed field checks env._protected
            self.assertTrue(industry.display_name)

        field = industry._fields["full_name"]
        with self.env.protecting([field], self.industry):
            self.assertTrue(industry.env.is_protected(field, industry))

    def test_pending_recomputations_are_restored(self):
        """Stored computed fields to recompute are recomputed after all."""
        currency = self.env["res.currency"].create(
            {"name": "ZZT", "symbol": "Z", "rounding": 0.01}
        )
        self.env.flush_all()
        field = currency._fields["decimal_places"]

        currency.rounding = 0.001
        self.assertTrue(self.env.is_to_compute(field, currency))
        with ThrowAwayCache(self.env):
            self.assertFalse(self.env.is_to_compute(field, currency))
            # The database still holds the value from before the update
            self.assertEqual(currency.decimal_places, 2)
        self.assertTrue(self.env.is_to_compute(field, currency))

        self.env.flush_all()
        self.assertEqual(
            self.env.execute_query(
                SQL(
                    "SELECT decimal_places FROM res_currency WHERE id = %s",
                    currency.id,
                )
            ),
            [(3,)],
        )
