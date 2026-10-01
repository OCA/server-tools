# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import UserError

from .common import DataImportCase


class RollbackTest(Exception):
    """Raised to roll a savepoint back without failing the test."""


class TestDataImportLog(DataImportCase):
    def test_new_log_is_pending(self):
        log = self._create_log()
        self.assertEqual(log.state, "pending")
        self.assertEqual(log.file_name, "feed.csv")
        self.assertTrue(log.date_start)
        self.assertFalse(log.date_done)

    def test_same_file_can_be_logged_twice(self):
        # A sender resends a file to correct a unit of it, so the same content
        # has to be able to come in again; what must not import twice is the
        # unit, which the module consuming the log recognizes.
        first = self._create_log()
        second = self._create_log()
        self.env.flush_all()
        self.assertEqual(first.content_hash, second.content_hash)
        self.assertEqual(second.state, "pending")

    def test_start_processing_sets_units(self):
        log = self._create_log()
        log._start_processing(3)
        self.assertEqual(log.state, "processing")
        self.assertEqual(log.unit_total, 3)
        self.assertEqual(log.unit_settled, 0)

    def test_start_processing_twice_is_rejected(self):
        log = self._create_log()
        log._start_processing(3)
        with self.assertRaises(UserError):
            log._start_processing(3)

    def test_settle_unit_counts_and_flags_the_last(self):
        log = self._create_log()
        log._start_processing(3)
        self.assertFalse(log._settle_unit())
        self.assertFalse(log._settle_unit(failed=True))
        self.assertTrue(log._settle_unit())
        self.assertEqual(log.unit_settled, 3)
        self.assertEqual(log.unit_failed, 1)

    def test_settle_unit_is_undone_by_a_rollback(self):
        log = self._create_log()
        log._start_processing(2)
        with self.assertRaises(RollbackTest), self.env.cr.savepoint(flush=False):
            log._settle_unit()
            self.assertEqual(log.unit_settled, 1)
            raise RollbackTest()
        log.invalidate_recordset(["unit_settled", "unit_failed"])
        self.assertEqual(log.unit_settled, 0)
