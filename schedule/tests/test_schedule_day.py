# © 2022 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import TransactionCase


class TestScheduleDay(TransactionCase):
    def test_01_weekly(self):
        sched = self.env["schedule.day"].create(
            {
                "name": "test_weekly",
                "weekday_ids": [(6, 0, [self.ref("schedule.schedule_weekday_monday")])],
                "start_date": date(2022, 5, 13),
                "mode": "weekly",
                "step": 2,
            }
        )

        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 14)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 15)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 16)), True)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 17)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 18)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 19)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 20)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 21)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 22)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 23)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 24)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 25)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 26)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 27)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 28)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 29)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 30)), True)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 31)), False)

    def test_02_monthly(self):
        sched = self.env["schedule.day"].create(
            {
                "name": "test_monthly",
                "weekday_ids": [
                    (
                        6,
                        0,
                        [
                            self.ref("schedule.schedule_weekday_wednesday"),
                            self.ref("schedule.schedule_weekday_friday"),
                        ],
                    )
                ],
                "start_date": date(2022, 5, 13),
                "mode": "monthly",
                "step": 1,
                "nth_weekday": "1",
            }
        )

        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 14)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 15)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 16)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 17)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 18)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 19)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 20)), False)

        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 1)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 2)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 3)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 4)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 5)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 6)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 7)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 8)), True)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 9)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 10)), True)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 11)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 12)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 13)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 14)), False)

    def test_03_yearly(self):
        sched = self.env["schedule.day"].create(
            {
                "name": "test_monthly",
                "weekday_ids": [
                    (
                        6,
                        0,
                        [
                            self.ref("schedule.schedule_weekday_saturday"),
                            self.ref("schedule.schedule_weekday_sunday"),
                        ],
                    )
                ],
                "start_date": date(2022, 5, 13),
                "mode": "yearly",
                "nth_weekday": "last",
                "yearly_month": "4",
            }
        )

        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 14)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 15)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 16)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 17)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 18)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 19)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 5, 20)), False)

        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 1)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 2)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 3)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 4)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 5)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 6)), False)
        self.assertEqual(sched.is_scheduled(day=date(2022, 6, 7)), False)

        self.assertEqual(sched.is_scheduled(day=date(2023, 4, 1)), False)
        self.assertEqual(sched.is_scheduled(day=date(2023, 4, 2)), False)
        self.assertEqual(sched.is_scheduled(day=date(2023, 4, 10)), False)
        self.assertEqual(sched.is_scheduled(day=date(2023, 4, 28)), False)
        self.assertEqual(sched.is_scheduled(day=date(2023, 4, 29)), True)
        self.assertEqual(sched.is_scheduled(day=date(2023, 4, 30)), True)
        self.assertEqual(sched.is_scheduled(day=date(2023, 5, 1)), False)
