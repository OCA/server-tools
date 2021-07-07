# Copyright 2021 Akretion - Chafique Delli
# Copyright 2021 Alfredo Zamora <alfredo.zamora@agilebg.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestSchedulerErrorMailer(TransactionCase):
    def setUp(self):
        super().setUp()
        self.cron = self.env.ref("scheduler_error_mailer.test_scheduler_error_mailer")
        self.cron.email_template_id.write({"auto_delete": False})
        self.cr.commit()  # pylint: disable=invalid-commit

    @mute_logger("odoo.addons.base.models.ir_cron", "UserError")
    def test_scheduler_failure(self):
        self.cron._callback(
            self.cron.name, self.cron.ir_actions_server_id.id, self.cron.id
        )
        mails = self.env["mail.mail"].search(
            [
                ("res_id", "=", self.cron.id),
                ("model", "=", "ir.cron"),
                ("message_type", "=", "email"),
            ]
        )
        self.assertEqual(len(mails), 1)
        subject = (
            "[DB " + self.cr.dbname + "] Scheduler 'Test Scheduler Error Mailer' FAILED"
        )
        self.assertEqual(mails.subject, subject)
