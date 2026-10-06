# Copyright 2026 Mayur Bechara <becharamayur49@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, fields, models
from odoo.exceptions import AccessError


class ChatGPTOAuthWizard(models.TransientModel):
    _name = "ai.chatgpt.oauth.wizard"
    _description = "ChatGPT Subscription Connection Wizard"

    state = fields.Selection(
        selection=[
            ("authorizing", "Waiting for Authorization"),
            ("done", "Connected Successfully"),
            ("error", "Error"),
        ],
        default="authorizing",
        string="State",
    )

    user_code = fields.Char(string="One-Time Code", readonly=True)
    verification_url = fields.Char(
        string="Verification URL",
        readonly=True,
        default="https://auth.openai.com/codex/device",
    )
    device_auth_id = fields.Char(string="Device Auth ID", readonly=True)
    interval = fields.Integer(string="Poll Interval", default=5)
    account_id = fields.Char(string="ChatGPT Account ID", readonly=True)
    status_message = fields.Text(string="Status Message", readonly=True)

    def _ensure_settings_admin(self):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Only Settings administrators can connect AI credentials."))

    def action_verify_and_complete(self):
        """Poll OpenAI for user approval and exchange for tokens."""
        self.ensure_one()
        self._ensure_settings_admin()
        result = self.env["ai.chatgpt.oauth"].poll_and_exchange(self.device_auth_id, self.user_code)

        if result.get("status") == "success":
            self.write({
                "state": "done",
                "account_id": result.get("account_id", ""),
                "status_message": _(
                    "ChatGPT is connected for AI chat and agents. "
                    "Knowledge sources and voice features use the optional OpenAI API key."
                ),
            })
            return {
                "name": _("Connect ChatGPT Subscription"),
                "type": "ir.actions.act_window",
                "res_model": self._name,
                "res_id": self.id,
                "view_mode": "form",
                "target": "new",
            }

        elif result.get("status") == "pending":
            self.write({
                "status_message": _("Authorization pending: Please open the verification link, enter code '%s', and approve in your browser before clicking Verify.") % self.user_code,
            })
            return {
                "name": _("Connect ChatGPT Subscription"),
                "type": "ir.actions.act_window",
                "res_model": self._name,
                "res_id": self.id,
                "view_mode": "form",
                "target": "new",
            }

        else:
            self.write({
                "state": "error",
                "status_message": result.get("message") or _("Authorization failed or expired. Please retry."),
            })
            return {
                "name": _("Connect ChatGPT Subscription"),
                "type": "ir.actions.act_window",
                "res_model": self._name,
                "res_id": self.id,
                "view_mode": "form",
                "target": "new",
            }

    def action_retry(self):
        """Restart the device authorization flow."""
        self.ensure_one()
        self._ensure_settings_admin()
        auth_data = self.env["ai.chatgpt.oauth"].initiate_device_auth()
        self.write({
            "state": "authorizing",
            "device_auth_id": auth_data["device_auth_id"],
            "user_code": auth_data["user_code"],
            "verification_url": auth_data["verification_url"],
            "interval": auth_data["interval"],
            "status_message": False,
        })
        return {
            "name": _("Connect ChatGPT Subscription"),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
