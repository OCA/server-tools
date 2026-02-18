# Copyright 2026 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from unittest.mock import patch

from odoo.tests import TransactionCase


class TestAutovacuumTunning(TransactionCase):
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

    def test_tune_creates_record_for_res_partner(self):
        # Set low thresholds to ensure res_partner exceeds them
        self._set_thresholds(vacuum_threshold=9, analyze_threshold=5)
        # Mock the method to return res_partner as exceeding the thresholds
        with patch.object(
            self.env.registry["database.autovacuum.tuning"],
            "_get_tables_exceeding_dead_tuples",
            return_value=[("public", "res_partner", 10)],
        ):
            self.env["database.autovacuum.tuning"]._db_autovacuum_tune()
        record = self.env["database.autovacuum.tuning"].search(
            [("name", "=", "public.res_partner")],
            limit=1,
        )

        self.assertTrue(record)
