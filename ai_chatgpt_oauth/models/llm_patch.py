# Copyright 2026 Mayur Bechara <becharamayur49@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import json
import logging
import requests

from odoo import _
from odoo.exceptions import UserError
from odoo.addons.ai.utils.llm_api_service import LLMApiService
from odoo.addons.ai.utils import llm_providers

from .chatgpt_models import get_chatgpt_models, get_chatgpt_model_ids

_logger = logging.getLogger(__name__)


def validate_chatgpt_model(env, model_name: str) -> str:
    """Validate model selection against active/cached ChatGPT models."""
    if not model_name:
        raise UserError(env._("Select a model on the AI Agent before using ChatGPT."))
    valid_ids = get_chatgpt_model_ids(env)
    if valid_ids and model_name not in valid_ids:
        _logger.warning(
            "Model '%s' is not in the cached ChatGPT models list. Attempting to use it directly.",
            model_name,
        )
    return model_name


# Preserve the standard OpenAI chat implementation. Embeddings, transcription,
# and realtime keep using the unmodified API-key methods on LLMApiService.
_orig_request_llm_openai_helper = LLMApiService._request_llm_openai_helper


def _get_chatgpt_error_message(event_data):
    """Extract a user-friendly message from ChatGPT response events."""
    response = event_data.get("response") or {}
    error = event_data.get("error") or (response.get("error") if isinstance(response, dict) else None)
    err_text = ""
    if isinstance(error, dict):
        err_text = error.get("message") or error.get("code") or json.dumps(error)
    elif error:
        err_text = str(error)
    else:
        err_text = event_data.get("message") or _("The ChatGPT response failed.")

    err_lower = err_text.lower()
    if "model" in err_lower and ("not found" in err_lower or "deprecated" in err_lower or "unsupported" in err_lower):
        return _(
            "OpenAI Error: %s. The selected model may be deprecated or unsupported by your subscription. "
            "Please sync models in AI Settings and update the model on your AI Agent."
        ) % err_text

    return err_text


def patched_request_llm_openai_helper(self, body, tools=None, inputs=()):
    ICP = self.env["ir.config_parameter"].sudo()
    auth_mode = ICP.get_param("ai.openai_auth_mode") or "api_key"

    if self.provider == "openai" and auth_mode == "oauth":
        access_token, account_id = self.env["ai.chatgpt.oauth"].get_valid_access_token()
        if not access_token or not account_id:
            raise UserError(_(
                "ChatGPT subscription is selected for AI chat but is not connected. "
                "Connect the ChatGPT subscription in AI Settings or switch chat routing to the OpenAI API key."
            ))

        body = dict(body)
        body["store"] = False
        body["stream"] = True

        # The ChatGPT subscription response route does not accept temperature.
        body.pop("temperature", None)

        # Validate model selection
        body["model"] = validate_chatgpt_model(self.env, body.get("model", ""))

        headers = {
            "Authorization": f"Bearer {access_token}",
            "chatgpt-account-id": account_id,
            "originator": "odoo",
            "User-Agent": "odoo/19.0",
            "Content-Type": "application/json",
            "OpenAI-Beta": "responses=experimental",
            "accept": "text/event-stream",
        }

        route = "https://chatgpt.com/backend-api/codex/responses"
        res = None
        try:
            res = requests.post(
                route,
                json=body,
                headers=headers,
                stream=True,
                timeout=(15, 300),
            )
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    err_json = e.response.json()
                    error_msg = err_json.get("detail") or err_json.get("error", {}).get("message") or e.response.text
                except Exception:
                    error_msg = e.response.text or str(e)
            _logger.warning("ChatGPT subscription request failed: %s", error_msg)
            raise UserError(error_msg)

        to_call = []
        response_texts = []
        next_inputs = list(inputs or ())
        request_token_usage = {}
        has_tool_calls = False
        completed = False

        try:
            for line in res.iter_lines():
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

                event_type = event_data.get("type", "")
                if event_type in ("error", "response.failed"):
                    raise UserError(_get_chatgpt_error_message(event_data))
                if event_type in ("response.incomplete", "response.cancelled"):
                    raise UserError(_get_chatgpt_error_message(event_data))

                # Output item completed (Message or Function Call)
                if event_type == "response.output_item.done":
                    item = event_data.get("item", {})
                    item_type = item.get("type")

                    if item_type == "function_call":
                        has_tool_calls = True
                        tool_name = item.get("name", "")
                        call_id = item.get("call_id") or item.get("id")
                        args_str = item.get("arguments", "{}")
                        try:
                            args = json.loads(args_str)
                        except (TypeError, ValueError):
                            args = {}
                        to_call.append((tool_name, call_id, args))
                        next_inputs.append(item)

                    elif item_type == "message":
                        content_list = item.get("content", [])
                        for part in content_list:
                            if part.get("type") == "output_text" and part.get("text"):
                                response_texts.append(part["text"])

                elif event_type == "response.completed":
                    completed = True
                    resp = event_data.get("response", {})
                    if resp.get("status") == "failed":
                        raise UserError(_get_chatgpt_error_message(event_data))
                    usage = resp.get("usage", {})
                    if usage:
                        request_token_usage["input_tokens"] = usage.get("input_tokens", 0)
                        request_token_usage["cached_tokens"] = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
                        request_token_usage["output_tokens"] = usage.get("output_tokens", 0)
        except requests.exceptions.RequestException as e:
            raise UserError(_("The ChatGPT response stream was interrupted: %s") % e) from e
        finally:
            res.close()

        if not completed and not response_texts and not to_call:
            raise UserError(_("ChatGPT ended the response before returning any output."))

        # If tools were called, return tool call list; otherwise return text response
        if has_tool_calls:
            return [], to_call, next_inputs, request_token_usage
        return response_texts, [], next_inputs, request_token_usage

    return _orig_request_llm_openai_helper(self, body, tools=tools, inputs=inputs)


# Apply monkey patch
LLMApiService._request_llm_openai_helper = patched_request_llm_openai_helper
_logger.info("Installed dynamic hybrid ChatGPT subscription routing on LLMApiService")
