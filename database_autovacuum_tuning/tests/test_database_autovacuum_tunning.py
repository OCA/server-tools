# Copyright 2026 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import TransactionCase


class TestAutovacuumTunning(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.cr.execute("CREATE EXTENSION IF NOT EXISTS pgstattuple")
        with cls.env.registry.cursor() as cr:
            cr._cnx.autocommit = True
            cr.execute("VACUUM (FULL, ANALYZE) res_partner")

    def _set_thresholds(self, vacuum_threshold=1, analyze_threshold=1):
        params = self.env["ir.config_parameter"].sudo()
        params.set_param(
            "database_autovacuum_tuning.autovacuum_vacuum_max_threshold",
            str(vacuum_threshold),
        )
        params.set_param(
            "database_autovacuum_tuning.autovacuum_vacuum_analyze_max_threshold",
            str(analyze_threshold),
        )

    def _generate_dead_tuples_on_res_partner(self, target_dead_tuples=10):
        partners = self.env["res.partner"].search([], limit=target_dead_tuples)
        if partners:
            self.env.cr.execute(
                "UPDATE res_partner SET name = name || ' (autovacuum test)' "
                "WHERE id = ANY(%s)",
                (partners.ids,),
            )
        self.env.flush_all()
        self.env.cr.execute("ANALYZE res_partner")

    def _get_dead_tuples(self, schemaname="public", tablename="res_partner"):
        table = f"{schemaname}.{tablename}"
        self.env.cr.execute(
            "SELECT dead_tuple_count FROM pgstattuple(%s::regclass)",
            (table,),
        )
        row = self.env.cr.fetchone()
        return row[0] if row else 0

    def test_tune_creates_record_for_res_partner(self):
        # Generate some dead tuples and set low thresholds to trigger tuning
        self.assertEqual(self._get_dead_tuples(), 0)
        self._generate_dead_tuples_on_res_partner(target_dead_tuples=10)
        self.assertEqual(self._get_dead_tuples(), 10)
        self._set_thresholds(vacuum_threshold=9, analyze_threshold=5)

        # Trigger the tuning method
        self.env["database.autovacuum.tuning"]._tune()
        record = self.env["database.autovacuum.tuning"].search(
            [("name", "=", "public.res_partner")],
            limit=1,
        )
        self.assertTrue(record)
