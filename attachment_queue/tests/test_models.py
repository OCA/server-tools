# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models
from odoo.exceptions import UserError


class AttachmentQueue(models.Model):
    _inherit = "attachment.queue"
    _name = "attachment.queue"

    def mock_run_fail(self):
        raise UserError(_("boom"))

    def mock_run_create_partners(self):
        for x in range(10):
            self.env["res.partner"].create({"name": str(x)})

    def mock_run_create_partners_and_fail(self):
        self.mock_run_create_partners()
        raise UserError(_("boom"))

    def _get_failure_emails(self):
        return "test@test.com"
