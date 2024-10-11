# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestTimeWindow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner 1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "partner 2"})
        cls.TimeWindow = cls.env["test.partner.time.window"]
        cls.monday = cls.env.ref("base_time_window.time_weekday_monday")
        cls.sunday = cls.env.ref("base_time_window.time_weekday_sunday")

    def test_00(self):
        """
        Data:
            A partner without time window
        Test Case:
            Add a time window
        Expected result:
            A time window is created for the partner
        """

        self.assertFalse(self.partner_1.time_window_ids)
        self.TimeWindow.create(
            {
                "partner_id": self.partner_1.id,
                "time_window_start": 10.0,
                "time_window_end": 12.0,
                "time_window_weekday_ids": [(4, self.monday.id)],
            }
        )
        self.assertTrue(self.partner_1.time_window_ids)
        time_window = self.partner_1.time_window_ids
        self.assertEqual(time_window.time_window_start, 10.0)
        self.assertEqual(time_window.time_window_end, 12.0)
        self.assertEqual(time_window.time_window_weekday_ids, self.monday)

    def test_01(self):
        """
        Data:
            A partner without time window
        Test Case:
            1 Add a time window
            2 unlink the partner
        Expected result:
            1 A time window is created for the partner
            2 The time window is removed
        """
        partner_id = self.partner_1.id
        self.assertFalse(self.partner_1.time_window_ids)
        self.TimeWindow.create(
            {
                "partner_id": self.partner_1.id,
                "time_window_start": 10.0,
                "time_window_end": 12.0,
                "time_window_weekday_ids": [(4, self.monday.id)],
            }
        )
        self.assertTrue(self.partner_1.time_window_ids)
        time_window = self.TimeWindow.search([("partner_id", "=", partner_id)])
        self.assertTrue(time_window)
        self.partner_1.unlink()
        self.assertFalse(time_window.exists())

    def test_02(self):
        """
        Data:
            A partner without time window
        Test Case:
            1 Add a time window
            2 Add a second time window that overlaps the first one (same day)
        Expected result:
            1 A time window is created for the partner
            2 ValidationError is raised
        """
        self.TimeWindow.create(
            {
                "partner_id": self.partner_1.id,
                "time_window_start": 10.0,
                "time_window_end": 12.0,
                "time_window_weekday_ids": [(4, self.monday.id)],
            }
        )
        with self.assertRaises(ValidationError):
            self.TimeWindow.create(
                {
                    "partner_id": self.partner_1.id,
                    "time_window_start": 11.0,
                    "time_window_end": 13.0,
                    "time_window_weekday_ids": [
                        (4, self.monday.id),
                        (4, self.sunday.id),
                    ],
                }
            )

    def test_03(self):
        """
        Data:
            A partner without time window
        Test Case:
            1 Add a time window
            2 Add a second time window that overlaps the first one (another day)
        Expected result:
            1 A time window is created for the partner
            2 A second  time window is created for the partner
        """
        self.assertFalse(self.partner_1.time_window_ids)
        self.TimeWindow.create(
            {
                "partner_id": self.partner_1.id,
                "time_window_start": 10.0,
                "time_window_end": 12.0,
                "time_window_weekday_ids": [(4, self.monday.id)],
            }
        )
        self.assertTrue(self.partner_1.time_window_ids)
        self.TimeWindow.create(
            {
                "partner_id": self.partner_1.id,
                "time_window_start": 11.0,
                "time_window_end": 13.0,
                "time_window_weekday_ids": [(4, self.sunday.id)],
            }
        )
        self.assertEqual(len(self.partner_1.time_window_ids), 2)

    def test_04(self):
        """
        Data:
            Partner 1 without time window
            Partner 2 without time window
        Test Case:
            1 Add a time window to partner 1
            2 Add the same time window to partner 2
        Expected result:
            1 A time window is created for the partner 1
            1 A time window is created for the partner 2
        """
        self.assertFalse(self.partner_1.time_window_ids)
        self.TimeWindow.create(
            {
                "partner_id": self.partner_1.id,
                "time_window_start": 10.0,
                "time_window_end": 12.0,
                "time_window_weekday_ids": [(4, self.monday.id)],
            }
        )
        self.assertTrue(self.partner_1.time_window_ids)
        self.assertFalse(self.partner_2.time_window_ids)
        self.TimeWindow.create(
            {
                "partner_id": self.partner_2.id,
                "time_window_start": 10.0,
                "time_window_end": 12.0,
                "time_window_weekday_ids": [(4, self.monday.id)],
            }
        )
        self.assertTrue(self.partner_2.time_window_ids)

    def test_05(self):
        """ ""
        Data:
            Partner 1 without time window
        Test Case:
            Add a time window to partner 1 with end > start
        Expected result:
            ValidationError is raised
        """
        with self.assertRaises(ValidationError):
            self.TimeWindow.create(
                {
                    "partner_id": self.partner_1.id,
                    "time_window_start": 14.0,
                    "time_window_end": 12.0,
                    "time_window_weekday_ids": [(4, self.monday.id)],
                }
            )

    def test_06(self):
        """ ""
        Data:
            Partner 1 with time window on monday
            Partner 2 with time window on monday
        Test Case:
            Change time window from Partner 1 to Partner 2
        Expected result:
            ValidationError is raised
        """
        self.assertFalse(self.partner_1.time_window_ids)
        p1_timewindow = self.TimeWindow.create(
            {
                "partner_id": self.partner_1.id,
                "time_window_start": 10.0,
                "time_window_end": 12.0,
                "time_window_weekday_ids": [(4, self.monday.id)],
            }
        )
        self.assertTrue(self.partner_1.time_window_ids)
        self.assertFalse(self.partner_2.time_window_ids)
        self.TimeWindow.create(
            {
                "partner_id": self.partner_2.id,
                "time_window_start": 10.0,
                "time_window_end": 12.0,
                "time_window_weekday_ids": [(4, self.monday.id)],
            }
        )
        self.assertTrue(self.partner_2.time_window_ids)
        with self.assertRaises(ValidationError):
            p1_timewindow.partner_id = self.partner_2

    def test_07(self):
        """
        Data:
            A partner without time window
        Test Case:
            1 Add a time window with stop hour > 23:59
            2 Add a time window with start hour > 23:59
        Expected result:
            ValidationError is raised
        """
        exception_regex = "Hour should be between 00 and 23"
        with self.assertRaisesRegex(ValidationError, exception_regex):
            self.TimeWindow.create(
                {
                    "partner_id": self.partner_1.id,
                    "time_window_start": 0.0,
                    "time_window_end": 27.0,
                    "time_window_weekday_ids": [(4, self.monday.id)],
                }
            )
        with self.assertRaisesRegex(ValidationError, exception_regex):
            self.TimeWindow.create(
                {
                    "partner_id": self.partner_1.id,
                    "time_window_start": 25.0,
                    "time_window_end": 27.0,
                    "time_window_weekday_ids": [(4, self.monday.id)],
                }
            )
