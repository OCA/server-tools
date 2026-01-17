# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PasswordDisplayWizard(models.TransientModel):
    """Wizard to securely display generated passwords.

    This replaces sticky notifications with a modal dialog that:
    - Is automatically closed when navigating away
    - Cannot be copied from browser history
    - Provides clear copy-to-clipboard functionality
    """

    _name = "mail.server.password.wizard"
    _description = "Password Display Wizard"

    password = fields.Char(
        string="Generated Password",
        readonly=True,
        help="This password will only be shown once. Please copy it now.",
    )
    mail_account_id = fields.Many2one(
        "mail.server.account",
        string="Mail Account",
        readonly=True,
    )
    email = fields.Char(
        string="Email Address",
        related="mail_account_id.email",
        readonly=True,
    )

    def action_copy_password(self):
        """Button to help user copy password (JS will handle actual copy)."""
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("Password Copied"),
                "message": self.env._(
                    "Password copied to clipboard. Please store it securely."
                ),
                "type": "success",
                "sticky": False,
            },
        }

    def action_close(self):
        """Close the wizard."""
        return {"type": "ir.actions.act_window_close"}
