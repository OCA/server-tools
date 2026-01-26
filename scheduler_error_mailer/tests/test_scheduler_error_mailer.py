# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.scheduler_error_mailer.hooks import post_init_hook


class TestSchedulerErrorMailer(BaseCommon):
    def setUp(self):
        super().setUp()
        self.cron = self.env["ir.cron"].create(
            {
                "name": "Test Scheduler Error Mailer",
                "active": False,
                "user_id": self.env.ref("base.user_root").id,
                "interval_number": 1,
                "interval_type": "hours",
                "model_id": self.env.ref("base.model_ir_cron").id,
                "state": "code",
                "code": "model._test_scheduler_failure()",
            }
        )

    def test_error_cron(self):
        with (
            self.assertLogs(
                "odoo.addons.scheduler_error_mailer.models.ir_cron", "DEBUG"
            ),
            patch.object(self.env.cr, "rollback"),
        ):
            self.cron._handle_callback_exception(
                self.cron.name,
                self.cron.ir_actions_server_id.id,
                Exception("hello world"),
            )

    def test_init_hook(self):
        post_init_hook(self.env)
        self.assertFalse(
            self.env["ir.cron"].search([("email_template_id", "=", False)])
        )
