# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from unittest.mock import MagicMock, patch

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestIrCron(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cron_model = cls.env.ref("base.model_res_partner")
        cls.base_cron_vals = {
            "state": "code",
            "code": "model._test_cron_method()",
            "model_id": cls.cron_model.id,
            "model_name": "res.partner",
            "user_id": cls.env.uid,
            "active": True,
            "interval_number": 1,
            "interval_type": "days",
            "nextcall": fields.Datetime.now() + timedelta(hours=1),
            "lastcall": False,
            "priority": 5,
        }
        cls.cron1 = cls.env["ir.cron"].create(
            {
                **cls.base_cron_vals,
                "name": "Test Cron 1",
            }
        )
        cls.cron2 = cls.env["ir.cron"].create(
            {
                **cls.base_cron_vals,
                "name": "Test Cron 2",
            }
        )

    def test_check_auto_exclusion_self_reference(self):
        """Test that a cron job cannot be mutually exclusive with itself"""
        with self.assertRaises(ValidationError):
            self.cron1.mutually_exclusive_cron_ids = self.cron1.ids

    def test_lock_mutually_exclusive_cron(self):
        """Test that FOR UPDATE NOWAIT is issued only when exclusive crons are found.

        Uses mocks because _lock_mutually_exclusive_cron opens a new DB connection
        that cannot see uncommitted test data.
        """
        mock_cr = MagicMock()
        mock_db = MagicMock()
        mock_db.cursor.return_value = mock_cr

        # With exclusive crons: expect FOR UPDATE NOWAIT
        mock_cr.fetchall.return_value = [(self.cron2.id,)]
        with patch("odoo.sql_db.db_connect", return_value=mock_db):
            result_cr = self.env["ir.cron"]._lock_mutually_exclusive_cron(
                self.env.cr, self.cron1.id
            )
        self.assertEqual(result_cr, mock_cr)
        self.assertEqual(mock_cr.execute.call_count, 2)
        self.assertIn("FOR UPDATE NOWAIT", mock_cr.execute.call_args_list[1][0][0])

        # Without exclusive crons: no FOR UPDATE NOWAIT
        mock_cr.reset_mock()
        mock_cr.fetchall.return_value = []
        with patch("odoo.sql_db.db_connect", return_value=mock_db):
            self.env["ir.cron"]._lock_mutually_exclusive_cron(
                self.env.cr, self.cron1.id
            )
        self.assertEqual(mock_cr.execute.call_count, 1)

    def test_process_job_releases_lock_on_exception(self):
        """Test that the lock cursor is closed even if the job raises an exception."""
        mock_lock_cr = MagicMock()
        job = {"id": self.cron1.id, "cron_name": self.cron1.name}
        IrCron = type(self.env["ir.cron"])

        with (
            patch.object(
                IrCron, "_lock_mutually_exclusive_cron", return_value=mock_lock_cr
            ),
            patch(
                "odoo.addons.base.models.ir_cron.IrCron._process_job",
                side_effect=RuntimeError("job failed"),
            ),
        ):
            with self.assertRaises(RuntimeError):
                IrCron._process_job(self.env.cr, job)

        mock_lock_cr.close.assert_called_once()
