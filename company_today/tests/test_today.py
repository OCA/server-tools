# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import SavepointCase


class TestToday(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.ref("base.main_company")

    def test_today(self):
        self.company.cron_update_today()
        self.assertEqual(self.company.today, fields.Date.today())

    @freeze_time("2022-02-22")
    def test_today_different_day(self):
        self.company.cron_update_today()
        self.assertEqual(self.company.today, fields.Date.today())
