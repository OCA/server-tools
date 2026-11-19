# Copyright 2026 Mayur Bechara <becharamayur49@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import json
import time
from unittest.mock import MagicMock, patch

from odoo.addons.ai.utils.llm_api_service import LLMApiService
from odoo.addons.ai_chatgpt_oauth.models import chatgpt_models, chatgpt_oauth, llm_patch
from odoo.exceptions import AccessError, UserError
from odoo.service.model import get_public_method
from odoo.tests import TransactionCase, new_test_user, tagged


class _FakeStreamResponse:
    def __init__(self, events):
        self._events = events
        self.closed = False
        self.text = ""

    def raise_for_status(self):
        return None

    def iter_lines(self):
        for event in self._events:
            yield b"data: " + json.dumps(event).encode()
        yield b"data: [DONE]"

    def close(self):
        self.closed = True


@tagged("post_install", "-at_install")
class TestHybridOpenAIRouting(TransactionCase):

    def setUp(self):
        super().setUp()
        self.icp = self.env["ir.config_parameter"].sudo()
        self.icp.set_param("ai.openai_key", "sk-standard-api")
        self.icp.set_param("ai.openai_auth_mode", "oauth")
        self.icp.set_param("ai.openai_oauth_access_token", "oauth-access-token")
        self.icp.set_param("ai.openai_oauth_refresh_token", "oauth-refresh-token")
        self.icp.set_param("ai.openai_oauth_expires_at", str(int(time.time()) + 3600))
        self.icp.set_param("ai.openai_chatgpt_account_id", "chatgpt-account")
        self.icp.set_param("ai.openai_chatgpt_cached_models", "")

    def test_supporting_services_keep_standard_api_key_in_mixed_mode(self):
        service = LLMApiService(self.env, provider="openai")

        self.assertEqual(service._get_api_token(), "sk-standard-api")
        self.assertEqual(service._get_base_headers()["Authorization"], "Bearer sk-standard-api")

        with patch.object(service, "_request", return_value={"data": [{"embedding": [0.1]}]}) as request:
            service.get_embedding("question", dimensions=1)
            self.assertEqual(request.call_args.kwargs["endpoint"], "/embeddings")
            self.assertEqual(
                request.call_args.kwargs["headers"]["Authorization"],
                "Bearer sk-standard-api",
            )

        with patch.object(service, "_request", return_value={"text": "transcript"}) as request:
            service.get_transcription(b"audio"), "transcript"
            self.assertEqual(request.call_args.kwargs["endpoint"], "/audio/transcriptions")
            self.assertEqual(
                request.call_args.kwargs["headers"]["Authorization"],
                "Bearer sk-standard-api",
            )

        with patch.object(service, "_request", return_value={"value": "client-secret"}) as request:
            service.get_transcription_session({})
            self.assertEqual(request.call_args.kwargs["endpoint"], "/realtime/client_secrets")
            self.assertEqual(
                request.call_args.kwargs["headers"]["Authorization"],
                "Bearer sk-standard-api",
            )

    def test_chat_uses_selected_agent_model_with_chatgpt_subscription(self):
        output_event = {
            "type": "response.output_item.done",
            "item": {
                "type": "message",
                "content": [{"type": "output_text", "text": "Hybrid routing works"}],
            },
        }
        completed_event = {
            "type": "response.completed",
            "response": {
                "status": "completed",
                "usage": {"input_tokens": 5, "output_tokens": 3},
            },
        }
        response = _FakeStreamResponse([output_event, completed_event])
        service = LLMApiService(self.env, provider="openai")

        with patch.object(llm_patch.requests, "post", return_value=response) as post:
            result = service._request_llm_openai_helper({
                "model": "gpt-5.5",
                "input": [{"role": "user", "content": "Hello"}],
                "temperature": 0.2,
            })

        self.assertEqual(result[0], ["Hybrid routing works"])
        self.assertEqual(result[3], {"input_tokens": 5, "cached_tokens": 0, "output_tokens": 3})
        self.assertTrue(response.closed)
        self.assertEqual(post.call_args.args[0], "https://chatgpt.com/backend-api/codex/responses")
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer oauth-access-token")
        self.assertEqual(post.call_args.kwargs["headers"]["chatgpt-account-id"], "chatgpt-account")
        self.assertNotIn("temperature", post.call_args.kwargs["json"])
        self.assertEqual(post.call_args.kwargs["json"]["model"], "gpt-5.5")

    def test_chatgpt_stream_failure_is_not_returned_as_empty_success(self):
        response = _FakeStreamResponse([{
            "type": "response.failed",
            "response": {"error": {"message": "Subscription limit reached"}},
        }])
        service = LLMApiService(self.env, provider="openai")

        with patch.object(llm_patch.requests, "post", return_value=response):
            with self.assertRaisesRegex(UserError, "Subscription limit reached"):
                service._request_llm_openai_helper({"model": "gpt-5.5", "input": []})

        self.assertTrue(response.closed)

    def test_missing_oauth_never_falls_back_to_paid_api_chat(self):
        self.icp.set_param("ai.openai_oauth_access_token", "")
        service = LLMApiService(self.env, provider="openai")

        with patch.object(llm_patch.requests, "post") as post:
            with self.assertRaisesRegex(UserError, "not connected"):
                service._request_llm_openai_helper({"model": "gpt-5.5", "input": []})

        post.assert_not_called()

    def test_sync_available_models_updates_cache_and_agent_selection(self):
        self.env["ai.chatgpt.model"].create({
            "name": "GPT-5.7 Pro",
            "code": "gpt-5.7-pro",
        })

        service = self.env["ai.chatgpt.oauth"]
        res = service.sync_available_models()

        self.assertEqual(res["status"], "success")
        self.assertIn("gpt-5.7-pro", [m[0] for m in res["models"]])

        # Check cached models via helper
        active_models = chatgpt_models.get_chatgpt_models(self.env)
        model_keys = [m[0] for m in active_models]
        self.assertIn("gpt-5.7-pro", model_keys)

        # Check agent selection includes synced model
        agent_selection = self.env["ai.agent"]._get_llm_model_selection()
        agent_model_keys = [m[0] for m in agent_selection]
        self.assertIn("gpt-5.7-pro", agent_model_keys)

    def test_settings_sync_models_action(self):
        settings = self.env["res.config.settings"].create({})
        action = settings.action_sync_chatgpt_models()

        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["params"]["type"], "success")
        self.assertIn("Successfully synchronized", action["params"]["message"])

    def test_oauth_service_methods_are_not_rpc_callable(self):
        service = self.env["ai.chatgpt.oauth"]
        for method_name in (
            "initiate_device_auth",
            "poll_and_exchange",
            "get_valid_access_token",
            "refresh_tokens",
            "sync_available_models",
            "disconnect",
            "test_connection",
        ):
            with self.subTest(method=method_name), self.assertRaises(AccessError):
                get_public_method(service, method_name)

    def test_internal_user_cannot_create_credential_wizard(self):
        internal_user = new_test_user(self.env, login="hybrid_ai_internal", groups="base.group_user")
        wizard_model = self.env["ai.chatgpt.oauth.wizard"].with_user(internal_user)

        with self.assertRaises(AccessError):
            wizard_model.check_access("create")
