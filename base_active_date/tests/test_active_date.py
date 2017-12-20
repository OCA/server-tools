# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime

from odoo.tests import common


class TestActiveDate(common.TransactionCase):

    def test_compute_active(self):
        """Test function for past, present and future active records."""
        test_model = self.env['active.date.test']
        # Create a record without start and end date. It should be active.
        forever_active = test_model.create({
            'code': 'FOREVER',
            'name': 'Record should be active forever'})
        self.assertTrue(forever_active.active)
        date_today = datetime.date.today()
        one_week = datetime.timedelta(days=7)
        date_last_week = date_today - one_week
        last_week = date_last_week.strftime("%Y-%m-%d")
        date_next_week = date_today + one_week
        next_week = date_next_week.strftime("%Y-%m-%d")
        # Create a record started before today, ends after today
        now_active = test_model.create({
            'code': 'NOW',
            'name': 'Record should be active now',
            'date_begin': last_week,
            'date_stop': next_week})
        self.assertTrue(now_active.active)
        # Create record that was active until last week
        last_week_active = test_model.create({
            'code': 'LAST WEEK',
            'name': 'Record was active until last week',
            'date_stop': last_week})
        self.assertFalse(last_week_active.active)
        # Create record that only will become active next week
        next_week_active = test_model.create({
            'code': 'NEXT WEEK',
            'name': 'Record will become active next week',
            'date_begin': next_week})
        self.assertFalse(next_week_active.active)
        # Make next week active record active from last_week
        next_week_active.write({'date_begin': last_week})
        self.assertTrue(next_week_active.active)
        # Set active to "wrong" values with SQL, than call cron job method.
        self.env.cr.execute(
            "UPDATE active_date_test SET active = false WHERE id = %s",
            (now_active.id, ))
        self.env.cr.execute(
            "UPDATE active_date_test SET active = true WHERE id = %s",
            (last_week_active.id, ))
        self.env.invalidate_all()  # Reset cache to force refresh from db
        self.assertTrue(last_week_active.active)
        self.assertFalse(now_active.active)
        test_model.active_date_refresh_all_cron()
        self.assertTrue(now_active.active)
        self.assertFalse(last_week_active.active)
