# Copyright 2026 Mayur Bechara <becharamayur49@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import datetime
import json
import os
import requests

from odoo import _, api, fields, models
from odoo.addons.ai.utils.llm_api_service import LLMApiService
from odoo.exceptions import AccessError, UserError
from odoo.tools import format_datetime

from .chatgpt_models import get_chatgpt_models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    openai_auth_mode = fields.Selection(
        selection=[
            ("api_key", "OpenAI API Key (Standard)"),
            ("oauth", "ChatGPT Subscription (OAuth)"),
        ],
        string="Connection Type",
        config_parameter="ai.openai_auth_mode",
        default="api_key",
        required=True,
        groups="base.group_system",
        help=(
            "Choose whether to connect via standard OpenAI API key or ChatGPT subscription. "
            "Embeddings, transcription, and realtime audio always use the standard OpenAI API key."
        ),
    )

    openai_oauth_connected = fields.Boolean(
        string="ChatGPT Connected",
        compute="_compute_openai_oauth_connected",
        groups="base.group_system",
    )
    openai_oauth_account_id = fields.Char(
        string="ChatGPT Account ID",
        compute="_compute_openai_oauth_connected",
        groups="base.group_system",
    )
    openai_oauth_expires_info = fields.Char(
        string="Session Status",
        compute="_compute_openai_oauth_connected",
        groups="base.group_system",
    )
    openai_oauth_synced_models_count = fields.Integer(
        string="Available Models Count",
        compute="_compute_openai_oauth_connected",
        groups="base.group_system",
    )
    openai_oauth_models_label = fields.Char(
        string="Synced Models Info",
        compute="_compute_openai_oauth_connected",
        groups="base.group_system",
    )
    openai_api_key_available = fields.Boolean(
        string="OpenAI API Key Available",
        compute="_compute_openai_api_key_available",
        groups="base.group_system",
    )

    def _ensure_settings_admin(self):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Only Settings administrators can manage AI credentials."))

    @api.depends("openai_key")
    def _compute_openai_key_enabled(self):
        ICP = self.env["ir.config_parameter"].sudo()
        has_oauth = bool(
            ICP.get_param("ai.openai_oauth_access_token")
            and ICP.get_param("ai.openai_oauth_refresh_token")
        )
        for record in self:
            record.openai_key_enabled = bool(record.openai_key or has_oauth)

    @api.depends("openai_key")
    def _compute_openai_api_key_available(self):
        for record in self:
            record.openai_api_key_available = bool(
                record.openai_key or os.getenv("ODOO_AI_CHATGPT_TOKEN")
            )

    def _compute_openai_oauth_connected(self):
        ICP = self.env["ir.config_parameter"].sudo()
        access_token = ICP.get_param("ai.openai_oauth_access_token")
        refresh_token = ICP.get_param("ai.openai_oauth_refresh_token")
        account_id = ICP.get_param("ai.openai_chatgpt_account_id") or ""
        try:
            expires_at = int(ICP.get_param("ai.openai_oauth_expires_at") or "0")
        except (TypeError, ValueError):
            expires_at = 0

        is_connected = bool(access_token and refresh_token)
        expires_str = ""
        if is_connected:
            expires_str = _("Session active • Auto-refreshes automatically")

        models_count = len(get_chatgpt_models(self.env))
        models_label = _("%d models synced") % models_count

        for record in self:
            record.openai_oauth_connected = is_connected
            record.openai_oauth_account_id = account_id
            record.openai_oauth_expires_info = expires_str
            record.openai_oauth_synced_models_count = models_count
            record.openai_oauth_models_label = models_label

    def action_open_chatgpt_oauth_wizard(self):
        """Open the ChatGPT OAuth Device Code connection wizard."""
        self.ensure_one()
        self._ensure_settings_admin()
        self.set_values()

        # Initiate device authorization code
        auth_data = self.env["ai.chatgpt.oauth"].initiate_device_auth()
        wizard = self.env["ai.chatgpt.oauth.wizard"].create({
            "state": "authorizing",
            "device_auth_id": auth_data["device_auth_id"],
            "user_code": auth_data["user_code"],
            "verification_url": auth_data["verification_url"],
            "interval": auth_data["interval"],
        })

        return {
            "name": _("Connect ChatGPT Subscription"),
            "type": "ir.actions.act_window",
            "res_model": "ai.chatgpt.oauth.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_disconnect_chatgpt_oauth(self):
        """Disconnect ChatGPT account."""
        self._ensure_settings_admin()
        self.env["ai.chatgpt.oauth"].disconnect()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ChatGPT Disconnected"),
                "message": _("The ChatGPT subscription has been disconnected. AI chat routing was changed to the OpenAI API key."),
                "type": "warning",
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    def action_test_chatgpt_oauth(self):
        """Test the ChatGPT subscription connection."""
        self._ensure_settings_admin()
        result = self.env["ai.chatgpt.oauth"].test_connection()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Connection Successful!"),
                "message": _("ChatGPT response: \"%s\"") % result.get("message", ""),
                "type": "success",
                "sticky": False,
            },
        }

    def action_sync_chatgpt_models(self):
        """Fetch active models from the ChatGPT backend endpoint."""
        self._ensure_settings_admin()
        res = self.env["ai.chatgpt.oauth"].sync_available_models()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Models Synchronized"),
                "message": _("Successfully synchronized %d ChatGPT models.") % res.get("count", 0),
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    def action_test_openai_api_key(self):
        """Validate the standard API credential without creating a billed model response."""
        self.ensure_one()
        self._ensure_settings_admin()
        self.set_values()
        token = LLMApiService(self.env, provider="openai")._get_api_token()
        response = None
        try:
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {token}"},
                timeout=15,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            if e.response is not None:
                try:
                    error = e.response.json().get("error") or {}
                    error_message = error.get("message") or e.response.text or error_message
                except (TypeError, ValueError):
                    error_message = e.response.text or error_message
            raise UserError(_("OpenAI API key test failed: %s") % error_message) from e
        finally:
            if response is not None:
                response.close()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("OpenAI API Key Verified"),
                "message": _("Embeddings, transcription, realtime, and API-based chat can use this credential."),
                "type": "success",
                "sticky": False,
            },
        }
