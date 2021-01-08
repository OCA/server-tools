# Copyright 2021 Akretion - Chafique Delli
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import SavepointCase


class TestSchedulerErrorMailer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_scheduler_error_mailer = cls.env.ref(
            "scheduler_error_mailer.test_scheduler_error_mailer"
        )

    def test_scheduler_failure(self):
        try:
            self.test_scheduler_error_mailer.method_direct_trigger()
        except Exception:
            pass
        lastcall = fields.Datetime.to_string(self.test_scheduler_error_mailer.lastcall)
        mails = self.env["mail.mail"].search(
            [
                ("res_id", "=", self.test_scheduler_error_mailer.id),
                ("model", "=", "ir.cron"),
                ("message_type", "=", "email"),
                ("date", "=", lastcall),
            ]
        )
        self.assertEqual(len(mails), 1)
        subject = (
            "[DB " + self.cr.dbname + "] Scheduler 'Test Scheduler Error Mailer' FAILED"
        )
        self.assertEqual(mails.subject, subject)
