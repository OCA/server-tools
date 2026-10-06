# Copyright 2026 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from datetime import datetime, timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCronWeekday(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cron = cls.env["ir.cron"].create(
            {
                "name": "Test Weekday Cron",
                "model_id": cls.env.ref("base.model_ir_cron").id,
                "state": "code",
                "code": "records = model",
                "interval_number": 1,
                "interval_type": "days",
                "nextcall": "2100-01-01 12:00:00",
            }
        )

    def _make_job(self, nextcall):
        return {
            "id": self.cron.id,
            "nextcall": nextcall,
            "interval_type": self.cron.interval_type,
            "interval_number": self.cron.interval_number,
        }

    def test_at_least_one_weekday_required(self):
        with self.assertRaises(ValidationError):
            self.cron.write(
                {
                    "run_monday": False,
                    "run_tuesday": False,
                    "run_wednesday": False,
                    "run_thursday": False,
                    "run_friday": False,
                    "run_saturday": False,
                    "run_sunday": False,
                }
            )

    def test_defer_off_disallowed_weekday(self):
        """A run landing on a deselected weekday moves to the next allowed day."""
        self.cron.write({"run_saturday": False, "run_sunday": False})
        saturday = datetime(2100, 1, 1, 12, 0, 0)
        while saturday.weekday() != 5:
            saturday += timedelta(days=1)
        self.cron._reschedule_later(self._make_job(saturday))
        self.cron.invalidate_recordset(["nextcall"])
        weekday = fields.Datetime.context_timestamp(
            self.cron, self.cron.nextcall
        ).weekday()
        self.assertNotIn(weekday, (5, 6), "nextcall still lands on a weekend")
        self.assertEqual(weekday, 0, "Saturday run should defer to Monday")

    def test_allowed_weekday_unchanged(self):
        """When all days are allowed, rescheduling behaves like core."""
        self.assertFalse(self.cron._disallowed_weekdays())
        past = datetime(2000, 1, 1, 12, 0, 0)
        now = self.env.cr.now()
        self.cron._reschedule_later(self._make_job(past))
        self.cron.invalidate_recordset(["nextcall"])
        self.assertGreater(
            self.cron.nextcall, now, "nextcall should advance into the future"
        )
