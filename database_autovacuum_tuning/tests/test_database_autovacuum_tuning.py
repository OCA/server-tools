# Copyright 2026 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from unittest.mock import patch

from odoo.tests import TransactionCase


class TestDatabaseAutovacuumTuning(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tuning_model = cls.env["database.autovacuum.tuning"]

    def _set_thresholds(self, vacuum_threshold="1", analyze_threshold="1"):
        """Set autovacuum threshold parameters for a test."""
        params = self.env["ir.config_parameter"].sudo()
        params.set_param(
            "database_autovacuum_tuning.autovacuum_vacuum_max_threshold",
            str(vacuum_threshold),
        )
        params.set_param(
            "database_autovacuum_tuning.autovacuum_vacuum_analyze_max_threshold",
            str(analyze_threshold),
        )

    def test_00_tune_creates_record_for_table(self):
        """Test tuning a table applies thresholds and records the operation."""
        self._set_thresholds(vacuum_threshold=9, analyze_threshold=5)
        with patch.object(
            type(self.tuning_model),
            "_get_tables_exceeding_dead_tuples",
            return_value=[("public", "res_partner", 10)],
        ) as get_tables:
            self.tuning_model._db_autovacuum_tune()

        get_tables.assert_called_once_with(9, 5)
        record = self.tuning_model.search(
            [("name", "=", "public.res_partner")],
            limit=1,
        )
        self.assertTrue(record)
        self.assertEqual(record.vacuum_threshold, 9)
        self.assertEqual(record.analyze_threshold, 5)

    def test_01_invalid_vacuum_threshold_disables_tuning(self):
        """Test an invalid vacuum threshold prevents table inspection."""
        self._set_thresholds(vacuum_threshold="invalid", analyze_threshold=5)
        with patch.object(
            type(self.tuning_model),
            "_get_tables_exceeding_dead_tuples",
        ) as get_tables:
            self.tuning_model._db_autovacuum_tune()

        get_tables.assert_not_called()

    def test_02_invalid_analyze_threshold_disables_tuning(self):
        """Test invalid and zero analyze thresholds disable tuning."""
        for analyze_threshold in ("invalid", 0):
            with self.subTest(analyze_threshold=analyze_threshold):
                self._set_thresholds(
                    vacuum_threshold=9,
                    analyze_threshold=analyze_threshold,
                )
                with patch.object(
                    type(self.tuning_model),
                    "_get_tables_exceeding_dead_tuples",
                ) as get_tables:
                    self.tuning_model._db_autovacuum_tune()

                get_tables.assert_not_called()

    def test_03_table_query_skips_current_reloptions(self):
        """Test table lookup skips settings matching both thresholds."""
        with (
            patch.object(self.env.cr, "execute") as execute,
            patch.object(self.env.cr, "fetchall", return_value=[]),
        ):
            self.tuning_model._get_tables_exceeding_dead_tuples(9, 5)

        query, params = execute.call_args.args
        self.assertIn("JOIN pg_class AS c", query)
        self.assertIn("COALESCE(c.reloptions, '{}') @> %s::text[]", query)
        self.assertEqual(
            params,
            (
                9,
                [
                    "autovacuum_vacuum_scale_factor=0",
                    "autovacuum_vacuum_threshold=9",
                    "autovacuum_analyze_scale_factor=0",
                    "autovacuum_analyze_threshold=5",
                ],
            ),
        )

    def test_04_cron_is_recurring(self):
        """Test the Odoo 17 scheduled action is configured to repeat."""
        cron = self.env.ref(
            "database_autovacuum_tuning.cron_database_autovacuum_tuning"
        )
        self.assertEqual(cron.numbercall, -1)
        self.assertFalse(cron.doall)
