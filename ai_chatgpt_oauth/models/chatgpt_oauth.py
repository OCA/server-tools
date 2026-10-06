# Copyright 2026 Mayur Bechara <becharamayur49@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import base64
import json
import logging
import time
import requests

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.addons.ai.utils import llm_providers

from .chatgpt_models import get_chatgpt_models

_logger = logging.getLogger(__name__)

CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
ISSUER = "https://auth.openai.com"
DEVICE_USER_CODE_URL = f"{ISSUER}/api/accounts/deviceauth/usercode"
DEVICE_TOKEN_URL = f"{ISSUER}/api/accounts/deviceauth/token"
TOKEN_URL = f"{ISSUER}/oauth/token"
DEVICE_REDIRECT_URI = f"{ISSUER}/deviceauth/callback"
CHATGPT_RESPONSES_ENDPOINT = "https://chatgpt.com/backend-api/codex/responses"
CHATGPT_MODELS_ENDPOINT = "https://chatgpt.com/backend-api/models"


def parse_jwt_claims(token):
    """Parse claims dictionary from a JWT without external libraries."""
    if not token or not isinstance(token, str):
        return {}
    parts = token.split(".")
    if len(parts) != 3:
        return {}
    payload = parts[1]
    padded = payload + "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode(padded)
        return json.loads(decoded.decode("utf-8"))
    except Exception as e:
        _logger.warning("Failed to decode JWT claims: %s", e)
        return {}


def extract_account_id(claims):
    """Extract ChatGPT Account ID from token claims."""
    if not isinstance(claims, dict):
        return False
    if claims.get("chatgpt_account_id"):
        return claims["chatgpt_account_id"]
    auth_claim = claims.get("https://api.openai.com/auth")
    if isinstance(auth_claim, dict) and auth_claim.get("chatgpt_account_id"):
        return auth_claim["chatgpt_account_id"]
    return False


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class ChatGPTOAuth(models.AbstractModel):
    _name = "ai.chatgpt.oauth"
    _description = "ChatGPT Subscription Authentication Service"

    @api.model
    @api.private
    def initiate_device_auth(self):
        """Initiate ChatGPT device authorization."""
        try:
            response = requests.post(
                DEVICE_USER_CODE_URL,
                json={"client_id": CLIENT_ID},
                headers={"Content-Type": "application/json", "User-Agent": "odoo/19.0"},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("device_auth_id") or not data.get("user_code"):
                raise UserError(_("OpenAI returned an incomplete device authorization response."))
            return {
                "device_auth_id": data.get("device_auth_id"),
                "user_code": data.get("user_code"),
                "interval": as_int(data.get("interval"), 5),
                "verification_url": f"{ISSUER}/codex/device",
            }
        except requests.exceptions.RequestException as e:
            _logger.error("Failed to initiate device auth: %s", e)
            raise UserError(_("Failed to start ChatGPT authentication: %s") % str(e))

    @api.model
    @api.private
    def poll_and_exchange(self, device_auth_id, user_code):
        """Poll device code approval and exchange for access tokens."""
        try:
            response = requests.post(
                DEVICE_TOKEN_URL,
                json={
                    "device_auth_id": device_auth_id,
                    "user_code": user_code,
                },
                headers={"Content-Type": "application/json", "User-Agent": "odoo/19.0"},
                timeout=15,
            )
            if response.status_code == 200:
                token_data = response.json()
                auth_code = token_data.get("authorization_code")
                code_verifier = token_data.get("code_verifier")
                if not auth_code or not code_verifier:
                    return {"status": "error", "message": _("Missing authorization code or verifier in response.")}

                return self._exchange_authorization_code(auth_code, code_verifier)

            if response.status_code in (403, 404):
                # Authorization pending
                return {"status": "pending"}

            error_text = response.text
            try:
                err_json = response.json()
                if "error" in err_json:
                    error_text = err_json.get("error_description") or err_json.get("error")
            except Exception:
                pass
            return {"status": "error", "message": error_text or _("Authentication request failed.")}
        except requests.exceptions.RequestException as e:
            _logger.error("Device auth polling error: %s", e)
            return {"status": "error", "message": str(e)}

    @api.model
    def _exchange_authorization_code(self, authorization_code, code_verifier):
        """Exchange authorization code for access and refresh tokens."""
        try:
            response = requests.post(
                TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": authorization_code,
                    "redirect_uri": DEVICE_REDIRECT_URI,
                    "client_id": CLIENT_ID,
                    "code_verifier": code_verifier,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "odoo/19.0"},
                timeout=20,
            )
            response.raise_for_status()
            tokens = response.json()

            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
            expires_in = as_int(tokens.get("expires_in"), 3600)
            id_token = tokens.get("id_token")

            if not access_token or not refresh_token:
                return {"status": "error", "message": _("Token exchange response missing access/refresh token.")}

            # Extract ChatGPT Account ID from id_token or access_token
            claims = parse_jwt_claims(id_token) if id_token else {}
            if not extract_account_id(claims):
                claims = parse_jwt_claims(access_token)
            account_id = extract_account_id(claims)
            if not account_id:
                return {
                    "status": "error",
                    "message": _("OpenAI did not return a ChatGPT account identifier. Please reconnect the account."),
                }

            # Save in config parameters
            ICP = self.env["ir.config_parameter"].sudo()
            ICP.set_param("ai.openai_auth_mode", "oauth")
            ICP.set_param("ai.openai_oauth_access_token", access_token)
            ICP.set_param("ai.openai_oauth_refresh_token", refresh_token)
            ICP.set_param("ai.openai_oauth_expires_at", str(int(time.time() + expires_in)))
            ICP.set_param("ai.openai_chatgpt_account_id", account_id)

            # Auto-sync live models from ChatGPT endpoint on connect
            try:
                self.sync_available_models()
            except Exception as sync_err:
                _logger.warning("Failed to auto-sync models after OAuth connect: %s", sync_err)

            return {
                "status": "success",
                "account_id": account_id,
            }
        except requests.exceptions.RequestException as e:
            _logger.error("Failed to exchange auth code: %s", e)
            return {"status": "error", "message": _("Failed to exchange tokens: %s") % str(e)}

    @api.model
    @api.private
    def get_valid_access_token(self):
        """Retrieve a valid OAuth access token, automatically refreshing if expired."""
        ICP = self.env["ir.config_parameter"].sudo()
        auth_mode = ICP.get_param("ai.openai_auth_mode") or "api_key"
        if auth_mode != "oauth":
            return None, None

        access_token = ICP.get_param("ai.openai_oauth_access_token")
        refresh_token = ICP.get_param("ai.openai_oauth_refresh_token")
        expires_at = as_int(ICP.get_param("ai.openai_oauth_expires_at"))
        account_id = ICP.get_param("ai.openai_chatgpt_account_id") or ""

        if not access_token or not refresh_token:
            return None, None

        # If expiring in less than 5 minutes (300s), refresh
        now = int(time.time())
        if expires_at - now < 300:
            _logger.info("ChatGPT OAuth token near expiry, refreshing...")
            success, access_token, account_id = self.refresh_tokens()
            if not success:
                _logger.warning("Automatic ChatGPT OAuth token refresh failed.")

        return access_token, account_id

    @api.model
    @api.private
    def refresh_tokens(self):
        """Refresh OAuth tokens using the stored refresh token."""
        # Serialize refreshes across Odoo workers. Refresh tokens may rotate, so
        # two workers must not exchange the same token concurrently.
        self.env.cr.execute(
            "SELECT pg_advisory_xact_lock(hashtext(%s))",
            ("ai_chatgpt_oauth.refresh",),
        )

        ICP = self.env["ir.config_parameter"].sudo()
        refresh_token = ICP.get_param("ai.openai_oauth_refresh_token")
        if not refresh_token:
            return False, None, None

        # A waiting worker rechecks the credentials after acquiring the lock.
        expires_at = as_int(ICP.get_param("ai.openai_oauth_expires_at"))
        access_token = ICP.get_param("ai.openai_oauth_access_token")
        account_id = ICP.get_param("ai.openai_chatgpt_account_id") or ""
        if access_token and account_id and expires_at - int(time.time()) >= 300:
            return True, access_token, account_id

        try:
            response = requests.post(
                TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": CLIENT_ID,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "odoo/19.0"},
                timeout=20,
            )
            response.raise_for_status()
            tokens = response.json()

            access_token = tokens.get("access_token")
            new_refresh_token = tokens.get("refresh_token") or refresh_token
            expires_in = as_int(tokens.get("expires_in"), 3600)
            id_token = tokens.get("id_token")

            if not access_token:
                return False, None, None

            # Extract account ID
            claims = parse_jwt_claims(id_token) if id_token else {}
            if not extract_account_id(claims):
                claims = parse_jwt_claims(access_token)
            account_id = extract_account_id(claims) or ICP.get_param("ai.openai_chatgpt_account_id")
            if not account_id:
                _logger.error("Refreshed ChatGPT token does not contain an account identifier.")
                return False, None, None

            ICP.set_param("ai.openai_oauth_access_token", access_token)
            ICP.set_param("ai.openai_oauth_refresh_token", new_refresh_token)
            ICP.set_param("ai.openai_oauth_expires_at", str(int(time.time() + expires_in)))
            ICP.set_param("ai.openai_chatgpt_account_id", account_id)

            # Keep models updated during refresh
            try:
                self.sync_available_models()
            except Exception as sync_err:
                _logger.debug("Failed to sync models on token refresh: %s", sync_err)

            return True, access_token, account_id
        except requests.exceptions.RequestException as e:
            _logger.error("Failed to refresh ChatGPT OAuth token: %s", e)
            return False, None, None

    @api.model
    @api.private
    def sync_available_models(self):
        """Verify connection and synchronize active ChatGPT models into provider registry."""
        access_token, account_id = self.get_valid_access_token()
        if not access_token or not account_id:
            raise UserError(_("Not connected to ChatGPT. Please connect your account first."))

        # Refresh provider cache from database records
        self.env["ai.chatgpt.model"]._refresh_provider_cache()
        active_models = self.env["ai.chatgpt.model"].sudo().search(
            [("active", "=", True)],
            order="sequence, id",
        )
        models_list = [(m.code, m.name) for m in active_models]

        _logger.info("Successfully synced %d models for ChatGPT subscription.", len(models_list))
        return {
            "status": "success",
            "count": len(models_list),
            "models": models_list,
        }

    @api.model
    @api.private
    def disconnect(self):
        """Clear OAuth credentials and revert auth mode to api_key."""
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("ai.openai_auth_mode", "api_key")
        ICP.set_param("ai.openai_oauth_access_token", "")
        ICP.set_param("ai.openai_oauth_refresh_token", "")
        ICP.set_param("ai.openai_oauth_expires_at", "0")
        ICP.set_param("ai.openai_chatgpt_account_id", "")
        ICP.set_param("ai.openai_chatgpt_cached_models", "")
        return True

    @api.model
    @api.private
    def test_connection(self):
        """Send a test prompt to verify the ChatGPT subscription connection."""
        access_token, account_id = self.get_valid_access_token()
        if not access_token or not account_id:
            raise UserError(_("Not connected to ChatGPT. Please connect your account first."))

        headers = {
            "Authorization": f"Bearer {access_token}",
            "chatgpt-account-id": account_id,
            "originator": "odoo",
            "User-Agent": "odoo/19.0",
            "Content-Type": "application/json",
            "OpenAI-Beta": "responses=experimental",
            "accept": "text/event-stream",
        }
        payload = {
            "model": "gpt-5.4-mini",
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Respond with 'Connection successful!'"}],
                }
            ],
            "store": False,
            "stream": True,
        }

        try:
            response = requests.post(
                CHATGPT_RESPONSES_ENDPOINT,
                json=payload,
                headers=headers,
                stream=True,
                timeout=30,
            )
            response.raise_for_status()

            reply_text = ""
            try:
                for line in response.iter_lines():
                    if not line:
                        continue
                    line_str = line.decode("utf-8")
                    if not line_str.startswith("data: "):
                        continue
                    data_str = line_str[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        event_data = json.loads(data_str)
                    except (TypeError, ValueError) as e:
                        raise UserError(_("ChatGPT returned an invalid streaming response.")) from e

                    event_type = event_data.get("type")
                    if event_type in ("error", "response.failed", "response.incomplete", "response.cancelled"):
                        error = event_data.get("error") or (event_data.get("response") or {}).get("error")
                        if isinstance(error, dict):
                            error = error.get("message") or error.get("code")
                        raise UserError(str(error or _("The ChatGPT connection test failed.")))

                    if event_type == "response.output_item.done":
                        item = event_data.get("item", {})
                        if item.get("type") == "message":
                            for part in item.get("content", []):
                                if part.get("type") == "output_text" and part.get("text"):
                                    reply_text += part["text"]
            finally:
                response.close()

            return {
                "success": True,
                "message": reply_text or _("Connection verified successfully!"),
                "account_id": account_id,
            }
        except requests.exceptions.RequestException as e:
            _logger.error("ChatGPT test connection failed: %s", e)
            err_msg = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    err_json = e.response.json()
                    err_msg = err_json.get("detail") or err_json.get("error", {}).get("message") or e.response.text
                except Exception:
                    err_msg = e.response.text or str(e)
            raise UserError(_("ChatGPT Connection Test Failed: %s") % err_msg)
