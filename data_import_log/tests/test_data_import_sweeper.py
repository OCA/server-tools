# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import timedelta
from unittest.mock import patch

from odoo import fields

from .common import DataImportCase

MODEL = "odoo.addons.data_import_log.models.data_import_log.DataImportLog"


class TestDataImportSweeper(DataImportCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))

    def _stuck_log(self, unit_total=2, minutes=120, **vals):
        log = self._create_log(**vals)
        log._start_processing(unit_total)
        log.date_start = fields.Datetime.now() - timedelta(minutes=minutes)
        return log

    def test_stuck_log_is_closed_as_failed(self):
        log = self._stuck_log()
        with patch(f"{MODEL}._import_unit", return_value=[]):
            log._run_unit("D-001", [])
        self.env["data.import.log"]._cron_sweep_stuck_logs()
        self.assertEqual(log.state, "partial")
        self.assertEqual(log.unit_settled, 2)
        self.assertEqual(log.unit_failed, 1)
        self.assertTrue(log.error_ids)

    def test_log_that_was_never_parsed_is_closed(self):
        log = self._create_log()
        log.date_start = fields.Datetime.now() - timedelta(minutes=120)
        self.assertEqual(log.state, "pending")
        self.env["data.import.log"]._cron_sweep_stuck_logs()
        self.assertEqual(log.state, "error")
        self.assertTrue(log.file_error)

    def test_recent_log_is_left_alone(self):
        log = self._stuck_log(minutes=5)
        self.env["data.import.log"]._cron_sweep_stuck_logs()
        self.assertEqual(log.state, "processing")

    def test_log_with_a_running_job_is_left_alone(self):
        log = self._stuck_log()
        self.env["queue.job"].create(
            {
                "uuid": "test-running-unit",
                "model_name": "data.import.log",
                "method_name": "_run_unit",
                "records": log,
                "args": (),
                "kwargs": {"unit_key": "D-001", "rows": []},
                "state": "started",
            }
        )
        self.env["data.import.log"]._cron_sweep_stuck_logs()
        self.assertEqual(log.state, "processing")

    def test_lost_finalizer_is_closed_without_failing_units(self):
        log = self._stuck_log(unit_total=1)
        with (
            patch(f"{MODEL}._import_unit", return_value=[]),
            patch(f"{MODEL}._enqueue_finalizer"),
        ):
            log._run_unit("D-001", [])
        self.assertEqual(log.state, "processing")
        self.env["data.import.log"]._cron_sweep_stuck_logs()
        self.assertEqual(log.state, "done")
        self.assertFalse(log.error_ids)

    def test_outcome_is_reported_on_the_log(self):
        log = self._stuck_log(unit_total=1)
        before = len(log.message_ids)
        errors = [{"reference": "D-001", "error_message": "unknown product"}]
        with patch(f"{MODEL}._import_unit", return_value=errors):
            log._run_unit("D-001", [])
        self.assertEqual(log.state, "error")
        self.assertGreater(len(log.message_ids), before)
        self.assertIn("unknown product", log.message_ids[0].body)

    def test_successful_import_is_not_reported(self):
        log = self._stuck_log(unit_total=1)
        before = len(log.message_ids)
        with patch(f"{MODEL}._import_unit", return_value=[]):
            log._run_unit("D-001", [])
        self.assertEqual(log.state, "done")
        self.assertEqual(len(log.message_ids), before)
