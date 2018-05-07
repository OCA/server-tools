# -*- coding: utf-8 -*-
# © 2018 Akretion <https://akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta
from pytz import timezone
import pytz
print "hi !"
class TestDST(TransactionCase):
    print "test ?"
    def test_dst(self):
        """First test, caching some data."""
        cron = self.env['ir.cron']
        brux = timezone('Europe/Brussels')
        ncall = -1
        winter_jan_12 = datetime(2018, 1, 1, 12, 0)
        winter_feb_0 = datetime(2018, 1, 2, 0, 0)
        summer_june_12 = datetime(2018, 6, 15, 12, 0)
        summer_sep_3 = datetime(2018, 9, 17, 3, 0)
        winter_jan_next_year = datetime(2019, 2,3, 0, 0)
        tests = [{
            'nextcall': brux.localize(winter_jan_12),
            'delta': timedelta(days=5),
            'now': brux.localize(winter_feb_0),
            'expected': timedelta(hours=0),
        }, {
            'nextcall': brux.localize(winter_jan_12),
            'delta': timedelta(days=6 * 30),
            'now': brux.localize(winter_feb_0),
            'expected': timedelta(hours=1),
        }, {
            'nextcall': brux.localize(winter_jan_12),
            'delta': timedelta(days=5),
            'now': brux.localize(summer_june_12),
            'expected': timedelta(hours=1),
        }, {
            'nextcall': brux.localize(winter_jan_12),
            'delta': timedelta(days=6 * 30),
            'now': brux.localize(summer_june_12),
            'expected': timedelta(hours=1),
        }, {
            'nextcall': brux.localize(winter_jan_12),
            'delta': timedelta(days=6 * 365),
            'now': brux.localize(winter_jan_next_year),
            'expected': timedelta(hours=0),
        }]
        tests = tests + [{
            'nextcall': brux.localize(summer_june_12),
            'delta': timedelta(days=5),
            'now': brux.localize(winter_jan_next_year),
            'expected': timedelta(hours=-1),
        }, {
            'nextcall': brux.localize(summer_june_12),
            'delta': timedelta(days=4 * 30),
            'now': brux.localize(winter_jan_next_year),
            'expected': timedelta(hours=-1),
        }, {
            'nextcall': brux.localize(summer_june_12),
            'delta': timedelta(days=5),
            'now': brux.localize(summer_june_12),
            'expected': timedelta(hours=0),
        }, {
            'nextcall': brux.localize(summer_june_12),
            'delta': timedelta(days=6 * 30),
            'now': brux.localize(summer_sep_3),
            'expected': timedelta(hours=-1),
        }, {
            'nextcall': brux.localize(summer_june_12),
            'delta': timedelta(days=6 * 365),
            'now': brux.localize(summer_sep_3),
            'expected': timedelta(hours=0),
        }]
        test = tests[0]
        for test in tests:
            res = cron._calculate_daylight_offset(
                test['nextcall'],
                test['delta'],
                ncall,
                test['now'])
            self.assertEqual(res, test['expected'])

