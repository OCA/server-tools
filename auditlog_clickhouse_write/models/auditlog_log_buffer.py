import json
import logging
from datetime import datetime, timezone
from typing import Any

from dateutil import parser as dt_parser

from odoo import api, fields, models
from odoo.tools import SQL

from odoo.addons.queue_job.exception import RetryableJobError

_logger = logging.getLogger(__name__)

JsonMapping = dict[str, Any]
ChRow = tuple[Any, ...]


class AuditlogLogBuffer(models.Model):
    """
    Buffered audit log payloads waiting to be flushed into ClickHouse.

    Each record stores a pre-built payload produced by the auditlog.rule override.
    Export is asynchronous:

      - A cron enqueues a queue_job.
      - The queue_job locks pending buffer rows (FOR UPDATE SKIP LOCKED),
        converts payloads to ClickHouse tuples and inserts them in batches.
      - Successfully flushed buffer rows are removed from PostgreSQL.

    Design notes:
      - This model is an internal queue; no user-facing ACLs should be provided.
      - queue_job provides retries/backoff when ClickHouse is slow/unavailable.
    """

    _name = "auditlog.log.buffer"
    _description = "Auditlog ClickHouse Buffer"
    _order = "create_date asc, id asc"

    STATE_PENDING = "pending"
    STATE_ERROR = "error"
    EXISTING_ROWS_CHUNK_SIZE = 2000

    # Column order MUST match CREATE TABLE schema and inserted tuples.
    _CH_LOG_COLUMNS: tuple[str, ...] = (
        "id",
        "name",
        "model_id",
        "model_name",
        "model_model",
        "res_id",
        "res_ids",
        "user_id",
        "method",
        "http_request_id",
        "http_session_id",
        "log_type",
        "create_date",
        "create_uid",
        "write_date",
        "write_uid",
    )
    _CH_LINE_COLUMNS: tuple[str, ...] = (
        "id",
        "log_id",
        "field_id",
        "field_name",
        "field_description",
        "old_value",
        "new_value",
        "old_value_text",
        "new_value_text",
        "create_date",
        "create_uid",
        "write_date",
        "write_uid",
    )
    _CH_HTTP_SESSION_COLUMNS: tuple[str, ...] = (
        "id",
        "user_id",
        "create_uid",
        "write_uid",
        "display_name",
        "name",
        "create_date",
        "write_date",
    )
    _CH_HTTP_REQUEST_COLUMNS: tuple[str, ...] = (
        "id",
        "user_id",
        "http_session_id",
        "create_uid",
        "write_uid",
        "display_name",
        "name",
        "root_url",
        "user_context",
        "create_date",
        "write_date",
    )

    _INVALID_PAYLOAD_MESSAGE = (
        "Invalid payload structure (expected object with 'log' and 'lines')."
    )

    @api.model
    def _selection_state(self):
        """Return centralized state selection values.

        :return: List of (value, label) tuples
        :rtype: List[Tuple[str, str]]
        """
        return [
            (self.STATE_PENDING, self.env._("Pending")),
            (self.STATE_ERROR, self.env._("Error")),
        ]

    payload_json = fields.Json(required=True)
    state = fields.Selection(
        selection=lambda self: self._selection_state(),
        default=lambda self: self.STATE_PENDING,
        required=True,
        index=True,
    )
    attempt_count = fields.Integer(default=0, required=True)
    error_message = fields.Text()

    @staticmethod
    def _to_ch_nullable_string(value):
        """Convert value to ClickHouse Nullable(String).

        Rules:
          - None/False -> None
          - str -> unchanged
          - list/dict/tuple -> JSON string
          - other -> str(value)

        :param value: Any value
        :type value: Any
        :return: Nullable string value
        :rtype: Optional[str]
        """
        if value is None or value is False:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, (dict | list | tuple)):
            return json.dumps(value, ensure_ascii=False, default=str)
        return str(value)

    @staticmethod
    def _to_ch_datetime_utc(value):
        """Convert value to timezone-aware UTC datetime.

        Normalizes to UTC for ClickHouse DateTime64(3, 'UTC').

        :param value: Incoming datetime or string
        :type value: Any
        :return: UTC-aware datetime or None
        :rtype: Optional[datetime]
        """
        if not value:
            return None

        if isinstance(value, datetime):
            parsed = value
        else:
            raw = str(value).strip().replace("Z", "+00:00")
            try:
                parsed = dt_parser.parse(raw)
            except (ValueError, TypeError, OverflowError):
                # Fallback: Odoo parser usually returns naive datetime.
                parsed = fields.Datetime.from_string(value)

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _ch_format_in_list(values):
        """Format a Python iterable as a ClickHouse IN (...) list.

        Used to build a safe-ish `IN (...)` fragment for identifiers when
        parametrization cannot be applied (e.g. identifiers in ClickHouse SQL).

        Rules:
          - None values are removed.
          - If all values are ints -> rendered without quotes.
          - Otherwise values are rendered as single-quoted strings with minimal
            escaping for backslashes and single quotes.

        :param values: Iterable of values (ints/strings) to include in IN list.
        :type values: Iterable[Any]
        :return: Comma-separated list content (without surrounding parentheses).
        :rtype: str
        """
        cleaned = [v for v in values if v is not None]
        if not cleaned:
            return ""
        # ints -> no quotes
        if all(isinstance(v, int) for v in cleaned):
            return ", ".join(str(v) for v in cleaned)

        # everything else -> single-quoted
        def _q(v):
            s = str(v).replace("\\", "\\\\").replace("'", "\\'")
            return f"'{s}'"

        return ", ".join(_q(v) for v in cleaned)

    @staticmethod
    def _chunk_values(values, chunk_size):
        """Yield chunks from a sequence.

        :param list values: Source values to split into chunks.
        :param int chunk_size: Maximum size of one chunk.
        :yield: Chunk of source values.
        :rtype: list
        """
        for index in range(0, len(values), chunk_size):
            yield values[index : index + chunk_size]

    def _filter_existing_rows(self, client, config, table_name, rows):
        """Filter out rows already present in ClickHouse by id.

        This helper makes inserts idempotent on retry: if part of a multi-table
        insert succeeds (e.g. auditlog_log) and another part fails (e.g. lines),
        the next retry must not re-insert already stored rows.

        The existence check is executed in chunks to avoid oversized ClickHouse
        queries caused by a very large ``IN (...)`` clause.

        :param client: ClickHouse client.
        :type client: clickhouse_driver.Client
        :param config: Active configuration (provides database name).
        :type config: AuditlogClickhouseConfig
        :param table_name: ClickHouse table name (without database prefix).
        :type table_name: str
        :param rows: Prepared ClickHouse rows.
        :type rows: List[ChRow]
        :return: Rows that are not yet present in ClickHouse.
        :rtype: List[ChRow]
        """
        if not rows:
            return rows

        ids = list(dict.fromkeys(row[0] for row in rows if row[0] is not None))
        if not ids:
            return rows

        existing_ids = set()
        for ids_chunk in self._chunk_values(ids, self.EXISTING_ROWS_CHUNK_SIZE):
            in_list = self._ch_format_in_list(ids_chunk)
            if not in_list:
                continue
            query = (
                f"SELECT id FROM {config.database}.{table_name} "
                f"WHERE id IN ({in_list})"
            )
            existing = client.execute(query) or []
            existing_ids.update(row[0] for row in existing)
        if not existing_ids:
            return rows
        return [row for row in rows if row[0] not in existing_ids]

    def _set_error(self, message):
        """Mark buffer records as error and increment attempt counter.

        :param message: Error message
        :type message: str
        """
        for rec in self:
            rec.write(
                {
                    "state": self.STATE_ERROR,
                    "attempt_count": rec.attempt_count + 1,
                    "error_message": message,
                }
            )

    @api.model
    def _lock_pending_buffers(self, batch_size):
        """Fetch and lock pending buffers using FOR UPDATE SKIP LOCKED.

        Prevents concurrent workers from selecting the same rows.

        :param batch_size: Maximum number of rows to fetch
        :type batch_size: int
        :return: Locked buffer recordset
        :rtype: AuditlogLogBuffer
        """
        query = SQL(
            """
            SELECT id
            FROM %s
            WHERE state = %s
            ORDER BY id
                FOR UPDATE SKIP LOCKED
                 LIMIT %s
            """,
            SQL.identifier(self._table),
            self.STATE_PENDING,
            batch_size,
        )
        self.env.cr.execute(query)
        ids = [row[0] for row in self.env.cr.fetchall()]
        return self.browse(ids)

    @api.model
    def _cron_flush_to_clickhouse(self, batch_size=None):
        """Schedule queue_job to flush buffered rows.

        Does not perform ClickHouse INSERT directly.

        :param batch_size: Optional override batch size
        :type batch_size: Optional[int]
        :return: True (cron compatibility)
        :rtype: bool
        """
        config = self.env["auditlog.clickhouse.config"].sudo().get_active_config()
        if not config:
            _logger.warning(
                "auditlog_clickhouse_write: cron flush " "skipped (no active config)"
            )
            return True

        effective_batch = int(batch_size or config.queue_batch_size or 0) or 1000

        if not self.sudo().search([("state", "=", self.STATE_PENDING)], limit=1):
            _logger.debug(
                "auditlog_clickhouse_write: cron flush skipped (no pending buffers)"
            )
            return True

        channel_name = (
            config.queue_channel_id.complete_name
            if config.queue_channel_id
            and getattr(config.queue_channel_id, "complete_name", None)
            else "root"
        )

        _logger.info(
            "auditlog_clickhouse_write: enqueue flush job "
            "(config=%s channel=%s batch_size=%s)",
            config.id,
            channel_name,
            effective_batch,
        )

        self.sudo().with_delay(
            channel=channel_name,
            description=f"auditlog_clickhouse_write: "
            f"flush buffers (config={config.id})",
        )._job_flush_to_clickhouse(config.id, effective_batch)

        return True

    @api.model
    def _get_active_config_for_job(self, config_id):
        """Return active config for job execution.

        :param config_id: Configuration record ID
        :type config_id: int
        :return: Active config or None
        :rtype: Optional[AuditlogClickhouseConfig]
        """
        config = self.env["auditlog.clickhouse.config"].sudo().browse(config_id)
        if not config or not config.exists() or not config.is_active:
            _logger.info(
                "auditlog_clickhouse_write: job skipped "
                "(config missing or not active) (config_id=%s)",
                config_id,
            )
            return None
        return config

    @classmethod
    def _payload_is_valid(cls, payload):
        """Validate payload structure before processing.

        Ensures minimal required fields exist to avoid endless retry loops.

        :param payload: Parsed JSON payload
        :type payload: Any
        :return: True if valid
        :rtype: bool
        """
        if not isinstance(payload, dict):
            return False

        log_data = payload.get("log")
        lines_data = payload.get("lines")
        http_session_data = payload.get("http_session")
        http_request_data = payload.get("http_request")

        if not isinstance(log_data, dict) or not isinstance(lines_data, list):
            return False
        if http_session_data is not None and not isinstance(http_session_data, dict):
            return False
        if http_request_data is not None and not isinstance(http_request_data, dict):
            return False

        # Minimal required log fields (to avoid CH insert failures forever)
        required = (
            "id",
            "model_id",
            "model_model",
            "user_id",
            "method",
            "create_date",
            "create_uid",
        )
        for key in required:
            if not log_data.get(key):
                return False

        # Lines must be a list of dicts (if any line is broken -> whole payload invalid)
        return all(isinstance(line, dict) for line in lines_data)

    def _collect_rows_from_buffers(self, buffers):
        """Extract ClickHouse rows from buffer payloads.

        :param buffers: Buffer recordset
        :type buffers: AuditlogLogBuffer
        :return: (
            valid_buffers,
            invalid_buffers,
            http_session_rows,
            http_request_rows,
            log_rows,
            line_rows,
        )
        :rtype: Tuple[
            AuditlogLogBuffer,
            AuditlogLogBuffer,
            List[ChRow],
            List[ChRow],
            List[ChRow],
            List[ChRow],
        ]
        """
        http_session_rows: list[ChRow] = []
        http_request_rows: list[ChRow] = []
        log_rows: list[ChRow] = []
        line_rows: list[ChRow] = []
        invalid_buffers = self.browse()

        for rec in buffers:
            payload = rec.payload_json

            if not self._payload_is_valid(payload):
                invalid_buffers |= rec
                continue

            http_session_data = payload.get("http_session")
            http_request_data = payload.get("http_request")
            log_data = payload["log"]
            lines_data = payload["lines"]

            if http_session_data:
                http_session_rows.append(
                    self._build_ch_http_session_row(http_session_data)
                )
            if http_request_data:
                http_request_rows.append(
                    self._build_ch_http_request_row(http_request_data)
                )

            log_rows.append(self._build_ch_log_row(log_data))
            for line_data in lines_data:
                line_rows.append(self._build_ch_line_row(line_data))

        valid_buffers = buffers - invalid_buffers
        return (
            valid_buffers,
            invalid_buffers,
            http_session_rows,
            http_request_rows,
            log_rows,
            line_rows,
        )

    def _mark_invalid_buffers(self, invalid_buffers, config):
        """Mark invalid payload buffers as error.

        :param invalid_buffers: Buffers to mark
        :type invalid_buffers: AuditlogLogBuffer
        :param config: Active configuration
        :type config: AuditlogClickhouseConfig
        """
        if not invalid_buffers:
            return
        invalid_buffers._set_error(self.env._(self._INVALID_PAYLOAD_MESSAGE))
        _logger.warning(
            "auditlog_clickhouse_write: invalid payloads=%s (marked error) (config=%s)",
            len(invalid_buffers),
            config.id,
        )

    def _insert_rows_to_clickhouse(
        self,
        client,
        config,
        http_session_rows,
        http_request_rows,
        log_rows,
        line_rows,
        valid_buffers,
    ):
        """Insert prepared rows into ClickHouse.

        Raises RetryableJobError on failure.

        :param client: ClickHouse client
        :type client: clickhouse_driver.Client
        :param config: Active configuration
        :type config: AuditlogClickhouseConfig
        :param log_rows: Rows for auditlog_log
        :type log_rows: List[ChRow]
        :param line_rows: Rows for auditlog_log_line
        :type line_rows: List[ChRow]
        :param valid_buffers: Successfully processed buffers
        :type valid_buffers: AuditlogLogBuffer
        """
        http_session_rows_to_insert = http_session_rows
        http_request_rows_to_insert = http_request_rows
        log_rows_to_insert = log_rows
        line_rows_to_insert = line_rows
        if http_session_rows:
            http_session_rows_to_insert = self._filter_existing_rows(
                client, config, "auditlog_http_session", http_session_rows
            )
        if http_request_rows:
            http_request_rows_to_insert = self._filter_existing_rows(
                client, config, "auditlog_http_request", http_request_rows
            )
        if log_rows:
            log_rows_to_insert = self._filter_existing_rows(
                client, config, "auditlog_log", log_rows
            )
        if line_rows:
            line_rows_to_insert = self._filter_existing_rows(
                client, config, "auditlog_log_line", line_rows
            )

        if (
            not http_session_rows_to_insert
            and not http_request_rows_to_insert
            and not log_rows_to_insert
            and not line_rows_to_insert
        ):
            _logger.warning(
                "auditlog_clickhouse_write: nothing to insert "
                "(config_id=%s buffers=%s)",
                config.id,
                len(valid_buffers),
            )
            return

        try:
            if http_session_rows_to_insert:
                client.execute(
                    f"INSERT INTO {config.database}.auditlog_http_session ("
                    f"{', '.join(self._CH_HTTP_SESSION_COLUMNS)}) VALUES",
                    http_session_rows_to_insert,
                )
            if http_request_rows_to_insert:
                client.execute(
                    f"INSERT INTO {config.database}.auditlog_http_request ("
                    f"{', '.join(self._CH_HTTP_REQUEST_COLUMNS)}) VALUES",
                    http_request_rows_to_insert,
                )
            if log_rows_to_insert:
                client.execute(
                    f"INSERT INTO {config.database}.auditlog_log ("
                    f"{', '.join(self._CH_LOG_COLUMNS)}) VALUES",
                    log_rows_to_insert,
                )
            if line_rows_to_insert:
                client.execute(
                    f"INSERT INTO {config.database}.auditlog_log_line ("
                    f"{', '.join(self._CH_LINE_COLUMNS)}) VALUES",
                    line_rows_to_insert,
                )
        except Exception as exc:
            _logger.exception(
                "auditlog_clickhouse_write: INSERT failed (will retry) "
                "(config=%s buffers=%s logs=%s lines=%s)",
                config.id,
                len(valid_buffers),
                len(log_rows_to_insert),
                len(line_rows_to_insert),
            )
            raise RetryableJobError(
                f"ClickHouse insert failed: {exc}",
                seconds=60,
            ) from exc

    def _delete_flushed_buffers(self, valid_buffers, config):
        """Delete flushed buffer rows from PostgreSQL.

        If deletion fails, mark them as error.

        :param valid_buffers: Buffers to delete
        :type valid_buffers: AuditlogLogBuffer
        :param config: Active configuration
        :type config: AuditlogClickhouseConfig
        """
        if not valid_buffers:
            _logger.warning(
                "auditlog_clickhouse_write: no flushed "
                "buffers to delete (config_id=%s)",
                config.id,
            )
            return

        try:
            valid_buffers.unlink()
        except Exception as exc:
            _logger.exception(
                "auditlog_clickhouse_write: failed to delete flushed buffers "
                "(config=%s buffers=%s)",
                config.id,
                len(valid_buffers),
            )
            valid_buffers._set_error(
                self.env._("Flushed to ClickHouse but failed to delete buffer rows: %s")
                % exc
            )
        else:
            _logger.info(
                "auditlog_clickhouse_write: job flushed batch "
                "(config=%s flushed_buffers=%s)",
                config.id,
                len(valid_buffers),
            )

    def _enqueue_next_flush_job_if_needed(self, config, batch_size):
        """Schedule next flush job if pending buffers remain.

        :param config: Active configuration
        :type config: AuditlogClickhouseConfig
        :param batch_size: Batch size
        :type batch_size: int
        """
        if not self.sudo().search([("state", "=", self.STATE_PENDING)], limit=1):
            return

        channel_name = (
            config.queue_channel_id.complete_name
            if config.queue_channel_id
            and getattr(config.queue_channel_id, "complete_name", None)
            else "root"
        )
        _logger.debug(
            "auditlog_clickhouse_write: more pending buffers detected, "
            "enqueue next job (config=%s channel=%s batch_size=%s)",
            config.id,
            channel_name,
            batch_size,
        )
        # NOTE: pass config.id (not recordset) to keep queue_job args JSON-serializable
        # and re-check config existence/is_active at execution time.
        self.sudo().with_delay(
            channel=channel_name,
            description=f"auditlog_clickhouse_write: "
            f"flush buffers (config={config.id})",
        )._job_flush_to_clickhouse(config.id, int(batch_size))

    @api.model
    def _job_flush_to_clickhouse(self, config_id, batch_size):
        """Queue job: flush one batch of buffers into ClickHouse.

        Steps:
          - Lock pending buffers
          - Validate payloads
          - Build CH rows
          - INSERT into ClickHouse (retryable)
          - Delete flushed buffers
          - Mark invalid buffers
          - Enqueue next batch if needed

        :param config_id: Active config ID
        :type config_id: int
        :param batch_size: Batch size
        :type batch_size: int
        """
        config = self._get_active_config_for_job(config_id)
        if not config:
            return

        pending_buffers = self.sudo()._lock_pending_buffers(int(batch_size))
        if not pending_buffers:
            _logger.debug(
                "auditlog_clickhouse_write: job no-op (no pending buffers) (config=%s)",
                config.id,
            )
            return

        (
            valid_buffers,
            invalid_buffers,
            http_session_rows,
            http_request_rows,
            log_rows,
            line_rows,
        ) = self._collect_rows_from_buffers(pending_buffers)

        # Nothing valid: just mark invalids and exit successfully.
        if not valid_buffers:
            self._mark_invalid_buffers(invalid_buffers, config)
            return

        client = config._get_client()
        self._insert_rows_to_clickhouse(
            client=client,
            config=config,
            http_session_rows=http_session_rows,
            http_request_rows=http_request_rows,
            log_rows=log_rows,
            line_rows=line_rows,
            valid_buffers=valid_buffers,
        )

        # Delete flushed buffers; if deletion fails,
        # mark them as error to avoid re-inserts.
        self._delete_flushed_buffers(valid_buffers, config)

        # Mark invalid ones only after successful CH insert
        # (so RetryableJobError doesn't rollback the marking)
        self._mark_invalid_buffers(invalid_buffers, config)

        # Continue draining queue
        self._enqueue_next_flush_job_if_needed(config, int(batch_size))

    @classmethod
    def _build_ch_http_session_row(cls, session_data):
        """Convert payload['http_session'] dict to ClickHouse tuple.

        :param session_data: HTTP session dictionary
        :type session_data: Dict[str, Any]
        :return: ClickHouse row tuple
        :rtype: ChRow
        """
        return (
            int(session_data.get("id") or 0),
            int(session_data.get("user_id") or 0)
            if session_data.get("user_id") is not None
            else None,
            int(session_data.get("create_uid") or 0)
            if session_data.get("create_uid") is not None
            else None,
            int(session_data.get("write_uid") or 0)
            if session_data.get("write_uid") is not None
            else None,
            cls._to_ch_nullable_string(session_data.get("display_name")),
            cls._to_ch_nullable_string(session_data.get("name")),
            cls._to_ch_datetime_utc(session_data.get("create_date")),
            cls._to_ch_datetime_utc(session_data.get("write_date")),
        )

    @classmethod
    def _build_ch_http_request_row(cls, request_data):
        """Convert payload['http_request'] dict to ClickHouse tuple.

        :param request_data: HTTP request dictionary
        :type request_data: Dict[str, Any]
        :return: ClickHouse row tuple
        :rtype: ChRow
        """
        return (
            int(request_data.get("id") or 0),
            int(request_data.get("user_id") or 0)
            if request_data.get("user_id") is not None
            else None,
            int(request_data.get("http_session_id") or 0)
            if request_data.get("http_session_id") is not None
            else None,
            int(request_data.get("create_uid") or 0)
            if request_data.get("create_uid") is not None
            else None,
            int(request_data.get("write_uid") or 0)
            if request_data.get("write_uid") is not None
            else None,
            cls._to_ch_nullable_string(request_data.get("display_name")),
            cls._to_ch_nullable_string(request_data.get("name")),
            cls._to_ch_nullable_string(request_data.get("root_url")),
            cls._to_ch_nullable_string(request_data.get("user_context")),
            cls._to_ch_datetime_utc(request_data.get("create_date")),
            cls._to_ch_datetime_utc(request_data.get("write_date")),
        )

    @classmethod
    def _build_ch_log_row(cls, log_data):
        """Convert payload['log'] dict to ClickHouse tuple.

        Order must match _CH_LOG_COLUMNS.

        :param log_data: Log dictionary
        :type log_data: Dict[str, Any]
        :return: ClickHouse row tuple
        :rtype: ChRow
        """
        return (
            int(log_data.get("id") or 0),
            cls._to_ch_nullable_string(log_data.get("name")),
            int(log_data.get("model_id") or 0),
            cls._to_ch_nullable_string(log_data.get("model_name")),
            (log_data.get("model_model") or "unknown"),
            int(log_data.get("res_id") or 0)
            if log_data.get("res_id") is not None
            else None,
            cls._to_ch_nullable_string(log_data.get("res_ids")),
            int(log_data.get("user_id") or 0),
            (log_data.get("method") or "unknown"),
            int(log_data.get("http_request_id") or 0)
            if log_data.get("http_request_id") is not None
            else None,
            int(log_data.get("http_session_id") or 0)
            if log_data.get("http_session_id") is not None
            else None,
            cls._to_ch_nullable_string(log_data.get("log_type")),
            cls._to_ch_datetime_utc(log_data.get("create_date")),
            int(log_data.get("create_uid") or 0),
            cls._to_ch_datetime_utc(log_data.get("write_date")),
            int(log_data.get("write_uid") or 0)
            if log_data.get("write_uid") is not None
            else None,
        )

    @classmethod
    def _build_ch_line_row(cls, line_data):
        """Convert payload['lines'][] dict to ClickHouse tuple.

        Order must match _CH_LINE_COLUMNS.

        :param line_data: Line dictionary
        :type line_data: Dict[str, Any]
        :return: ClickHouse row tuple
        :rtype: ChRow
        """
        return (
            int(line_data.get("id") or 0),
            int(line_data.get("log_id") or 0),
            int(line_data.get("field_id") or 0),
            cls._to_ch_nullable_string(line_data.get("field_name")),
            cls._to_ch_nullable_string(line_data.get("field_description")),
            cls._to_ch_nullable_string(line_data.get("old_value")),
            cls._to_ch_nullable_string(line_data.get("new_value")),
            cls._to_ch_nullable_string(line_data.get("old_value_text")),
            cls._to_ch_nullable_string(line_data.get("new_value_text")),
            cls._to_ch_datetime_utc(line_data.get("create_date")),
            int(line_data.get("create_uid") or 0),
            cls._to_ch_datetime_utc(line_data.get("write_date")),
            int(line_data.get("write_uid") or 0)
            if line_data.get("write_uid") is not None
            else None,
        )
