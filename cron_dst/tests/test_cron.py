# © 2022 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestCron(TransactionCase):
    def setUp(self):
        super().setUp()

        self.cron = self.env["ir.cron"].search([("active", "=", False)], limit=1)

    def test_flagging(self):
        self.assertEqual(self.cron.dst_offset, 0)

        self.cron.tz = False
        self.cron._onchange_dst()
        self.assertEqual(self.cron.dst_offset, 0)

        # A timezone with winter and summer time and an offset always > 0
        self.cron.tz = "Europe/Berlin"
        self.cron._onchange_dst()
        self.assertNotEqual(self.cron.dst_offset, 0)

    def test_adjustment(self):
        # A timezone with winter and summer time and an offset always > 0
        self.cron.tz = "Europe/Berlin"
        self.cron.dst_offset = 0

        # Lock is released and it should get adjusted
        self.cron._adjust_job_to_dst()
        self.assertNotEqual(self.cron.dst_offset, 0)
