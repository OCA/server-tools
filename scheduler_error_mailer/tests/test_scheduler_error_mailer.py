# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import TransactionCase

from odoo.addons.scheduler_error_mailer.hooks import post_init_hook


class TestSchedulerErrorMailer(TransactionCase):
    def setUp(self):
        super().setUp()
        self.cron = self.env.ref("scheduler_error_mailer.test_scheduler_error_mailer")

    def test_error_cron(self):
        with self.assertLogs(
            "odoo.addons.scheduler_error_mailer.models.ir_cron", "DEBUG"
        ), patch.object(self.env.cr, "rollback"):
            self.env["ir.cron"]._handle_callback_exception(
                self.cron.name,
                self.cron.ir_actions_server_id.id,
                self.cron.id,
                Exception("hello world"),
            )

    def test_init_hook(self):
        post_init_hook(self.env)
        self.assertFalse(
            self.env["ir.cron"].search([("email_template_id", "=", False)])
        )
