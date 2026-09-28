# Copyright (C) 2026 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timezone

from odoo import api, fields, models
from odoo.http import request


class AuditlogHTTPSession(models.Model):
    _inherit = "auditlog.http.session"

    @api.model
    def _is_clickhouse_write_enabled(self):
        """Return whether ClickHouse write mode is active."""
        return bool(self.env["auditlog.clickhouse.config"].sudo().get_active_config())

    @api.model
    def _ensure_http_session_sequence(self):
        """Ensure PostgreSQL sequence exists for HTTP session identifiers."""
        self.env.cr.execute(
            "CREATE SEQUENCE IF NOT EXISTS auditlog_http_session_id_seq"
        )

    @api.model
    def _next_http_session_id(self):
        """Return next PostgreSQL sequence value for HTTP session payload."""
        self._ensure_http_session_sequence()
        self.env.cr.execute("SELECT nextval('auditlog_http_session_id_seq')")
        return int(self.env.cr.fetchone()[0])

    @api.model
    def _build_http_session_payload(self, session_id):
        """Build in-memory payload for current HTTP session."""
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat(timespec="milliseconds")
        uid = request.uid or self.env.uid or 1
        user = self.env["res.users"].sudo().browse(uid)
        user_name = user.name if user.exists() else "?"
        display_name = f"{user_name} ({fields.Datetime.to_string(now_dt)})"

        return {
            "id": int(session_id),
            "user_id": int(uid) if uid else None,
            "create_uid": int(uid) if uid else None,
            "write_uid": None,
            "display_name": display_name,
            "name": request.session.sid,
            "create_date": now_iso,
            "write_date": None,
        }

    @api.model
    def _get_cached_http_session_payload(self, session_id=None):
        """Return cached current-request HTTP session payload if available."""
        if request and getattr(request, "session", None):
            payload = getattr(request.session, "auditlog_http_session_payload", None)
            if payload and (session_id is None or payload["id"] == session_id):
                return payload
        return None

    @api.model
    def current_http_session(self):
        """Return current HTTP session ID.

        In ClickHouse write mode, avoid ORM create() on auditlog_http_session
        and store the row as an in-memory payload cached on request.session.
        """
        if not self._is_clickhouse_write_enabled():
            return super().current_http_session()

        if not request:
            return False

        httpsession = request.session
        if not httpsession:
            return False

        payload = getattr(httpsession, "auditlog_http_session_payload", None)
        if payload:
            return payload["id"]

        session_id = getattr(httpsession, "auditlog_http_session_id", None)
        if not session_id:
            session_id = self._next_http_session_id()
            httpsession.auditlog_http_session_id = session_id

        payload = self._build_http_session_payload(session_id)
        httpsession.auditlog_http_session_payload = payload
        return session_id

    @api.model
    def get_clickhouse_payload(self, session_id=None):
        """Return HTTP session payload from cache or local database.

        :param session_id: Target HTTP session ID
        :type session_id: Optional[int]
        :return: Serialized HTTP session payload or None
        :rtype: Optional[dict]
        """
        payload = self._get_cached_http_session_payload(session_id)
        if payload:
            return payload

        if not session_id:
            return None

        session = self.sudo().browse(session_id)
        if not session.exists():
            return None

        return {
            "id": int(session.id),
            "user_id": int(session.user_id.id) if session.user_id else None,
            "create_uid": int(session.create_uid.id) if session.create_uid else None,
            "write_uid": int(session.write_uid.id) if session.write_uid else None,
            "display_name": session.display_name,
            "name": session.name,
            "create_date": session.create_date.isoformat()
            if session.create_date
            else None,
            "write_date": session.write_date.isoformat()
            if session.write_date
            else None,
        }
