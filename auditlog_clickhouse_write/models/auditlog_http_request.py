# Copyright (C) 2026 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timezone

from odoo import api, fields, models
from odoo.http import request


class AuditlogHTTPRequest(models.Model):
    _inherit = "auditlog.http.request"

    @api.model
    def _is_clickhouse_write_enabled(self):
        """Return whether ClickHouse write mode is active."""
        return bool(self.env["auditlog.clickhouse.config"].sudo().get_active_config())

    @api.model
    def _ensure_http_request_sequence(self):
        """Ensure PostgreSQL sequence exists for HTTP request identifiers."""
        self.env.cr.execute(
            "CREATE SEQUENCE IF NOT EXISTS auditlog_http_request_id_seq"
        )

    @api.model
    def _next_http_request_id(self):
        """Return next PostgreSQL sequence value for HTTP request payload."""
        self._ensure_http_request_sequence()
        self.env.cr.execute("SELECT nextval('auditlog_http_request_id_seq')")
        return int(self.env.cr.fetchone()[0])

    @api.model
    def _build_http_request_payload(self, request_id):
        """Build in-memory payload for current HTTP request."""
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat(timespec="milliseconds")
        uid = request.uid or self.env.uid or 1
        path = request.httprequest.path
        display_name = f"{path or '?'} ({fields.Datetime.to_string(now_dt)})"
        session_id = self.env["auditlog.http.session"].current_http_session() or None
        return {
            "id": int(request_id),
            "user_id": int(uid) if uid else None,
            "http_session_id": int(session_id) if session_id else None,
            "create_uid": int(uid) if uid else None,
            "write_uid": None,
            "display_name": display_name,
            "name": path,
            "root_url": request.httprequest.url_root,
            "user_context": request.context,
            "create_date": now_iso,
            "write_date": None,
        }

    @api.model
    def _get_cached_http_request_payload(self, request_id=None):
        """Return cached current-request HTTP request payload if available."""
        if request and getattr(request, "httprequest", None):
            payload = getattr(
                request.httprequest, "auditlog_http_request_payload", None
            )
            if payload and (request_id is None or payload["id"] == request_id):
                return payload
        return None

    @api.model
    def current_http_request(self):
        """Return current HTTP request ID.

        In ClickHouse write mode, avoid ORM create() on auditlog_http_request
        and store the row as an in-memory payload cached on request.httprequest.
        """
        if not self._is_clickhouse_write_enabled():
            return super().current_http_request()

        if not request:
            return False

        httprequest = request.httprequest
        if not httprequest:
            return False

        payload = getattr(httprequest, "auditlog_http_request_payload", None)
        if payload:
            return payload["id"]

        request_id = getattr(httprequest, "auditlog_http_request_id", None)
        if not request_id:
            request_id = self._next_http_request_id()
            httprequest.auditlog_http_request_id = request_id

        payload = self._build_http_request_payload(request_id)
        httprequest.auditlog_http_request_payload = payload
        return request_id

    @api.model
    def get_clickhouse_payload(self, request_id=None):
        """Return HTTP request payload from cache or local database.

        :param request_id: Target HTTP request ID
        :type request_id: Optional[int]
        :return: Serialized HTTP request payload or None
        :rtype: Optional[dict]
        """
        payload = self._get_cached_http_request_payload(request_id)
        if payload:
            return payload

        if not request_id:
            return None

        http_request = self.sudo().browse(request_id)
        if not http_request.exists():
            return None

        return {
            "id": int(http_request.id),
            "user_id": int(http_request.user_id.id) if http_request.user_id else None,
            "http_session_id": (
                int(http_request.http_session_id.id)
                if http_request.http_session_id
                else None
            ),
            "create_uid": int(http_request.create_uid.id)
            if http_request.create_uid
            else None,
            "write_uid": int(http_request.write_uid.id)
            if http_request.write_uid
            else None,
            "display_name": http_request.display_name,
            "name": http_request.name,
            "root_url": http_request.root_url,
            "user_context": http_request.user_context,
            "create_date": http_request.create_date.isoformat()
            if http_request.create_date
            else None,
            "write_date": http_request.write_date.isoformat()
            if http_request.write_date
            else None,
        }
