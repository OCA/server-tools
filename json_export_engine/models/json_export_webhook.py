# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import hashlib
import hmac
import json
import logging
import time
import uuid

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class JsonExportWebhook(models.Model):
    _name = "json.export.webhook"
    _description = "JSON Export Webhook"
    _order = "name"

    name = fields.Char(required=True)
    schema_id = fields.Many2one(
        "json.export.schema",
        string="Export Schema",
        required=True,
        ondelete="cascade",
    )
    active = fields.Boolean(default=True)
    url = fields.Char(required=True)
    on_create = fields.Boolean(default=True)
    on_write = fields.Boolean(default=True)
    on_unlink = fields.Boolean(string="On Delete", default=True)
    secret_key = fields.Char(
        help="HMAC-SHA256 signing key. If set, a X-Webhook-Signature "
        "header will be sent with each request.",
        groups="json_export_engine.group_manager",
    )
    header_ids = fields.One2many(
        "json.export.webhook.header",
        "webhook_id",
        string="Custom Headers",
    )
    max_retries = fields.Integer(default=3)
    async_delivery = fields.Boolean(
        default=False,
        help="When enabled and queue_job is installed, webhook delivery "
        "is processed asynchronously via a background job.",
    )
    state = fields.Selection(
        [
            ("active", "Active"),
            ("error", "Error"),
            ("paused", "Paused"),
        ],
        default="active",
        readonly=True,
    )
    last_call_date = fields.Datetime(readonly=True)
    last_call_status = fields.Char(readonly=True)

    def action_reset_state(self):
        """Reset webhook state to active."""
        self.write({"state": "active"})
        return True

    @api.model
    def _fire_for_model(self, model_name, event_type, records):
        """Find matching webhooks and fire them for the given model and event."""
        event_field = f"on_{event_type}"
        webhooks = self.search(
            [
                ("active", "=", True),
                ("state", "=", "active"),
                ("schema_id.active", "=", True),
                ("schema_id.model_name", "=", model_name),
                (event_field, "=", True),
            ]
        )
        for webhook in webhooks:
            try:
                webhook._trigger_webhook(event_type, records)
            except Exception:
                _logger.exception(
                    "Webhook '%s' failed for %s on %s",
                    webhook.name,
                    event_type,
                    model_name,
                )

    def _trigger_webhook(self, event_type, records):
        """Serialize records and send webhook payload."""
        self.ensure_one()
        delivery_id = str(uuid.uuid4())
        start_time = time.time()
        schema = self.schema_id
        try:
            if event_type == "unlink":
                # For deletions, send IDs only (records will be gone)
                data = [{"id": r.id} for r in records]
            else:
                data = schema._serialize_records(records)

            payload = {
                "event": event_type,
                "model": schema.model_name,
                "schema": schema.name,
                "timestamp": fields.Datetime.now().isoformat(),
                "delivery_id": delivery_id,
                "records": data,
            }

            # Async delivery via queue_job when available
            if self.async_delivery and hasattr(self, "with_delay"):
                self.with_delay(
                    description=f"Webhook: {self.name} ({event_type})",
                )._send_payload(payload, delivery_id=delivery_id)
                duration = int((time.time() - start_time) * 1000)
                self.sudo().write(
                    {
                        "last_call_date": fields.Datetime.now(),
                        "last_call_status": "queued",
                    }
                )
                schema._create_log(
                    "webhook",
                    "success",
                    len(records),
                    duration,
                    request_info=json.dumps(
                        {
                            "webhook": self.name,
                            "event": event_type,
                            "url": self.url,
                            "delivery_id": delivery_id,
                            "async": True,
                        }
                    ),
                )
                return

            self._send_payload(payload, delivery_id=delivery_id)
            duration = int((time.time() - start_time) * 1000)
            self.sudo().write(
                {
                    "last_call_date": fields.Datetime.now(),
                    "last_call_status": "success",
                }
            )
            schema._create_log(
                "webhook",
                "success",
                len(records),
                duration,
                request_info=json.dumps(
                    {
                        "webhook": self.name,
                        "event": event_type,
                        "url": self.url,
                        "delivery_id": delivery_id,
                    }
                ),
            )
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.sudo().write(
                {
                    "last_call_date": fields.Datetime.now(),
                    "last_call_status": f"error: {str(e)[:200]}",
                    "state": "error",
                }
            )
            schema._create_log(
                "webhook",
                "error",
                len(records),
                duration,
                error_message=str(e),
                request_info=json.dumps(
                    {
                        "webhook": self.name,
                        "event": event_type,
                        "url": self.url,
                        "delivery_id": delivery_id,
                    }
                ),
            )
            _logger.warning("Webhook '%s' failed: %s", self.name, e)

    def _send_payload(self, payload, delivery_id=None):
        """Send HTTP POST with optional HMAC signing and custom headers."""
        self.ensure_one()
        body = json.dumps(payload, ensure_ascii=False)
        headers = {"Content-Type": "application/json"}

        # Add custom headers
        for header in self.header_ids:
            headers[header.key] = header.value

        # Delivery ID for deduplication (set after custom headers so it
        # cannot be accidentally overwritten by a user-defined header)
        if delivery_id:
            headers["X-Delivery-ID"] = delivery_id

        # HMAC-SHA256 signature
        if self.secret_key:
            signature = hmac.new(
                self.secret_key.encode("utf-8"),
                body.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            headers["X-Webhook-Signature"] = signature

        # Send with retry
        last_error = None
        for attempt in range(max(self.max_retries, 1)):
            try:
                resp = requests.post(
                    self.url,
                    data=body,
                    headers=headers,
                    timeout=30,
                )
                resp.raise_for_status()
                return
            except requests.RequestException as e:
                _logger.warning(
                    "Webhook request failed (attempt %d/%d): webhook=%s, error=%s",
                    attempt + 1,
                    max(self.max_retries, 1),
                    self.name,
                    str(e),
                )
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s...
                    time.sleep(2**attempt)
        _logger.error(
            "Webhook request failed after all retries: webhook=%s, error=%s",
            self.name,
            str(last_error),
        )
        raise last_error
