# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import hashlib
import hmac
import json
import logging
import uuid
from unittest import mock

import requests

from .common import JsonExportTestCase


class _MissingAttribute:
    """Descriptor that raises AttributeError when accessed (for hasattr checks)."""

    def __get__(self, obj, objtype=None):
        raise AttributeError("with_delay")


class TestJsonExportWebhook(JsonExportTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.webhook = cls.env["json.export.webhook"].create(
            {
                "name": "Test Webhook",
                "schema_id": cls.schema.id,
                "url": "https://webhook.example.com/hook",
                "on_create": True,
                "on_write": True,
                "on_unlink": True,
                "secret_key": "test-secret-key",
                "max_retries": 2,
            }
        )
        cls.env["json.export.webhook.header"].create(
            {
                "webhook_id": cls.webhook.id,
                "key": "X-Custom-Header",
                "value": "custom-value",
            }
        )

    def _mock_post_success(self):
        """Return a mock for requests.post that succeeds."""
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        return mock.patch("requests.post", return_value=mock_response)

    def _mock_post_failure(self):
        """Return a mock for requests.post that always fails."""
        return mock.patch(
            "requests.post",
            side_effect=requests.ConnectionError("Connection refused"),
        )

    # -- _fire_for_model tests --

    def test_fire_for_model_create(self):
        """Fires webhook on create event."""
        with self._mock_post_success() as mock_post:
            self.env["json.export.webhook"]._fire_for_model(
                "res.partner", "create", self.partner1
            )
            mock_post.assert_called_once()

    def test_fire_for_model_write(self):
        """Fires webhook on write event."""
        with self._mock_post_success() as mock_post:
            self.env["json.export.webhook"]._fire_for_model(
                "res.partner", "write", self.partner1
            )
            mock_post.assert_called_once()

    def test_fire_for_model_unlink(self):
        """Fires webhook on unlink event."""
        with self._mock_post_success() as mock_post:
            self.env["json.export.webhook"]._fire_for_model(
                "res.partner", "unlink", self.partner1
            )
            mock_post.assert_called_once()

    def test_fire_for_model_disabled_event(self):
        """Does NOT fire when event flag is False."""
        self.webhook.on_create = False
        with self._mock_post_success() as mock_post:
            self.env["json.export.webhook"]._fire_for_model(
                "res.partner", "create", self.partner1
            )
            mock_post.assert_not_called()
        self.webhook.on_create = True

    def test_fire_for_model_inactive_webhook(self):
        """Does NOT fire for inactive webhooks."""
        self.webhook.active = False
        with self._mock_post_success() as mock_post:
            self.env["json.export.webhook"]._fire_for_model(
                "res.partner", "create", self.partner1
            )
            mock_post.assert_not_called()
        self.webhook.active = True

    # -- _trigger_webhook tests --

    def test_trigger_webhook_payload(self):
        """Payload contains required fields."""
        with self._mock_post_success() as mock_post:
            self.webhook._trigger_webhook("create", self.partner1)
            call_args = mock_post.call_args
            body = json.loads(call_args.kwargs.get("data", call_args[1].get("data")))
            self.assertEqual(body["event"], "create")
            self.assertEqual(body["model"], "res.partner")
            self.assertEqual(body["schema"], "Test Partners")
            self.assertIn("timestamp", body)
            self.assertIn("records", body)
            self.assertIsInstance(body["records"], list)

    def test_trigger_webhook_unlink_payload(self):
        """Unlink events send only record IDs."""
        with self._mock_post_success() as mock_post:
            self.webhook._trigger_webhook("unlink", self.partner1)
            call_args = mock_post.call_args
            body = json.loads(call_args.kwargs.get("data", call_args[1].get("data")))
            self.assertEqual(body["event"], "unlink")
            records = body["records"]
            self.assertEqual(len(records), 1)
            self.assertIn("id", records[0])
            self.assertEqual(records[0]["id"], self.partner1.id)

    # -- _send_payload tests --

    def test_send_payload_hmac(self):
        """X-Webhook-Signature header contains HMAC-SHA256."""
        with self._mock_post_success() as mock_post:
            payload = {"test": True}
            self.webhook._send_payload(payload)
            call_args = mock_post.call_args
            headers = call_args.kwargs.get("headers", call_args[1].get("headers"))
            self.assertIn("X-Webhook-Signature", headers)
            # Verify the signature matches
            body = json.dumps(payload, ensure_ascii=False)
            expected_sig = hmac.new(
                b"test-secret-key",
                body.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            self.assertEqual(headers["X-Webhook-Signature"], expected_sig)

    def test_send_payload_custom_headers(self):
        """Custom headers from header_ids are included."""
        with self._mock_post_success() as mock_post:
            self.webhook._send_payload({"test": True})
            call_args = mock_post.call_args
            headers = call_args.kwargs.get("headers", call_args[1].get("headers"))
            self.assertEqual(headers.get("X-Custom-Header"), "custom-value")

    def test_send_payload_retry_on_failure(self):
        """Retries up to max_retries on HTTP error."""
        with self._mock_post_failure() as mock_post, mock.patch("time.sleep"):
            logging.disable(logging.CRITICAL)
            try:
                with self.assertRaises(requests.RequestException):
                    self.webhook._send_payload({"test": True})
                self.assertEqual(mock_post.call_count, self.webhook.max_retries)
            finally:
                logging.disable(logging.NOTSET)

    def test_send_payload_state_on_error(self):
        """State changes to 'error' after all retries fail."""
        with self._mock_post_failure(), mock.patch("time.sleep"):
            logging.disable(logging.CRITICAL)
            try:
                self.webhook._trigger_webhook("create", self.partner1)
            finally:
                logging.disable(logging.NOTSET)
        self.assertEqual(self.webhook.state, "error")

    # -- Delivery ID / deduplication tests --

    def test_trigger_webhook_delivery_id_in_payload(self):
        """Payload contains a valid UUID delivery_id."""
        with self._mock_post_success() as mock_post:
            self.webhook._trigger_webhook("create", self.partner1)
            call_args = mock_post.call_args
            body = json.loads(call_args.kwargs.get("data", call_args[1].get("data")))
            self.assertIn("delivery_id", body)
            # Validate it's a proper UUID
            parsed = uuid.UUID(body["delivery_id"])
            self.assertEqual(str(parsed), body["delivery_id"])

    def test_send_payload_delivery_id_header(self):
        """X-Delivery-ID header is present when delivery_id is passed."""
        with self._mock_post_success() as mock_post:
            delivery_id = str(uuid.uuid4())
            self.webhook._send_payload({"test": True}, delivery_id=delivery_id)
            call_args = mock_post.call_args
            headers = call_args.kwargs.get("headers", call_args[1].get("headers"))
            self.assertEqual(headers.get("X-Delivery-ID"), delivery_id)

    def test_delivery_id_same_on_retry(self):
        """Same delivery_id is used across all retry attempts."""
        delivery_ids_seen = []

        def capture_post(*args, **kwargs):
            delivery_ids_seen.append(kwargs.get("headers", {}).get("X-Delivery-ID"))
            raise requests.ConnectionError("Connection refused")

        with mock.patch("requests.post", side_effect=capture_post):
            with mock.patch("time.sleep"):
                logging.disable(logging.CRITICAL)
                try:
                    with self.assertRaises(requests.RequestException):
                        self.webhook._send_payload(
                            {"test": True}, delivery_id="fixed-id-123"
                        )
                finally:
                    logging.disable(logging.NOTSET)
        self.assertEqual(len(delivery_ids_seen), self.webhook.max_retries)
        self.assertTrue(all(d == "fixed-id-123" for d in delivery_ids_seen))

    def test_delivery_id_in_log(self):
        """delivery_id is stored in log request_info."""
        with self._mock_post_success():
            self.webhook._trigger_webhook("create", self.partner1)
        log = self.env["json.export.log"].search(
            [
                ("schema_id", "=", self.schema.id),
                ("log_type", "=", "webhook"),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(log)
        info = json.loads(log.request_info)
        self.assertIn("delivery_id", info)
        # Validate it's a UUID
        uuid.UUID(info["delivery_id"])

    # -- Async delivery tests --

    def test_async_delivery_uses_with_delay(self):
        """When async_delivery=True and with_delay exists, it is called."""
        self.webhook.async_delivery = True
        mock_delayed = mock.MagicMock()
        with mock.patch.object(
            type(self.webhook), "with_delay", create=True, return_value=mock_delayed
        ):
            self.webhook._trigger_webhook("create", self.partner1)
            mock_delayed._send_payload.assert_called_once()

    def test_async_delivery_fallback_sync(self):
        """When async_delivery=True but with_delay is absent, falls back to sync."""
        self.webhook.async_delivery = True
        # Mock with_delay to raise AttributeError to simulate non-queue_job install
        webhook_class = type(self.webhook)
        with mock.patch.object(
            webhook_class, "with_delay", new=_MissingAttribute(), create=True
        ):
            with self._mock_post_success() as mock_post:
                self.webhook._trigger_webhook("create", self.partner1)
                mock_post.assert_called_once()

    # -- action_reset_state test --

    def test_action_reset_state(self):
        """Resets state back to 'active'."""
        self.webhook.sudo().write({"state": "error"})
        self.webhook.action_reset_state()
        self.assertEqual(self.webhook.state, "active")
