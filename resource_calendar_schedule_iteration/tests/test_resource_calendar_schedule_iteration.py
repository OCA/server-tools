# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

import odoo.tests.common as common


class TestResourceCalendarScheduleIteration(common.TransactionCase):

    def setUp(self):
        super(TestResourceCalendarScheduleIteration, self).setUp()

        self.icp = self.env['ir.config_parameter']

        self.calendar = self.env.ref('resource.resource_calendar_std')
        self.icp.set_param(
            "resource.calendar.schedule.days.iteration.limit", 200)

    def test_01_days_iteration(self):
        days = 150
        calendar_day = self.calendar.plan_days(-1 * days - 1, datetime.today())
        aprox_date = datetime.today() - timedelta(days=days)
        # Without more iteration limit the date returned will be only 100
        # days back using calendar (default iteration limit) instead of 150.
        self.assertLess(calendar_day, aprox_date)

    def test_02_hours_iteration(self):
        hours = 1500 * 8
        hours_2 = 1700 * 8
        limit_hour = self.calendar.plan_hours(-1 * hours - 1, datetime.today())
        limit_hour_2 = self.calendar.plan_hours(
            -1 * hours_2 - 1, datetime.today())
        # Both hour computation exceeded the limit so they should be the
        # same (which is incorrect).
        self.assertEqual(limit_hour, limit_hour_2)
        self.icp.set_param(
            "resource.calendar.schedule.hours.iteration.limit", 2000)
        correct_hour = self.calendar.plan_hours(
            -1 * hours - 1, datetime.today())
        correct_hour_2 = self.calendar.plan_hours(
            -1 * hours_2 - 1, datetime.today())
        self.assertNotEqual(correct_hour, correct_hour_2)
        self.assertLess(correct_hour, limit_hour)
        self.assertLess(correct_hour_2, limit_hour_2)
