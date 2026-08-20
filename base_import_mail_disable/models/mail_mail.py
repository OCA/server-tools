# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.model_create_multi
    def create(self, values_list):
        """
        Intercept hard-coded mail.mail record creations during mass imports.
        Instead of letting them queue normally, forcefully flag them as 'cancel'
        so the mail cron job inherently ignores them.
        """
        if self.env.context.get("import_file"):
            for vals in values_list:
                vals["state"] = "cancel"
                vals["auto_delete"] = False
        return super().create(values_list)

    def send(self, auto_commit=False, raise_exception=False, post_send_callback=None):
        """
        Intercept synchronous/immediate mail dispatch calls during mass imports.
        Simulate a successful dispatch by returning True, while protecting the
        SMTP server from spam.
        """
        if self.env.context.get("import_file"):
            return True
        return super().send(
            auto_commit=auto_commit,
            raise_exception=raise_exception,
            post_send_callback=post_send_callback,
        )
