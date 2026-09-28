import logging
import time
from collections.abc import Mapping
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, TypedDict

from odoo import models

from odoo.addons.auditlog.models.rule import EMPTY_DICT, FIELDS_BLACKLIST, DictDiffer

_logger = logging.getLogger(__name__)


class _PayloadLog(TypedDict, total=False):
    """Structured payload for auditlog_log row before buffering."""

    id: str
    name: str | None
    model_id: int
    model_name: str | None
    model_model: str
    res_id: int | None
    res_ids: str | None
    user_id: int
    method: str
    http_request_id: int | None
    http_session_id: int | None
    log_type: str | None
    create_date: str
    create_uid: int


class _PayloadLine(TypedDict, total=False):
    """Structured payload for auditlog_log_line row before buffering."""

    id: str
    log_id: str
    field_id: int
    field_name: str | None
    field_description: str | None
    old_value: Any | None
    new_value: Any | None
    old_value_text: Any | None
    new_value_text: Any | None
    create_date: str
    create_uid: int


class _PayloadHttpSession(TypedDict, total=False):
    """Structured payload for auditlog_http_session row before buffering."""

    id: int
    name: str | None
    user_id: int | None
    create_date: str | None
    create_uid: int | None
    write_date: str | None
    write_uid: int | None


class _PayloadHttpRequest(TypedDict, total=False):
    """Structured payload for auditlog_http_request row before buffering."""

    id: int
    name: str | None
    root_url: str | None
    user_id: int | None
    http_session_id: int | None
    user_context: Any | None
    create_date: str | None
    create_uid: int | None
    write_date: str | None
    write_uid: int | None


class _Payload(TypedDict, total=False):
    """Full payload stored in auditlog.log.buffer."""

    log: _PayloadLog
    lines: list[_PayloadLine]
    http_session: _PayloadHttpSession | None
    http_request: _PayloadHttpRequest | None


def _json_sanitize(obj):
    """Convert value to JSON-serializable structure.

    Handles:
      - datetime/date -> ISO string
      - Decimal -> float
      - bytes -> UTF-8 string
      - recordsets -> list of ids
      - mappings/sequences -> recursively sanitized
      - unknown types -> string representation

    :param obj: Arbitrary value
    :type obj: Any
    :return: JSON-safe value
    :rtype: Any
    """
    if obj is None or isinstance(obj, (str | int | float | bool)):
        return obj

    if isinstance(obj, (datetime | date)):
        return obj.isoformat()

    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")

    if isinstance(obj, models.BaseModel):
        return list(obj.ids)

    if isinstance(obj, Mapping):
        return {str(k): _json_sanitize(v) for k, v in obj.items()}

    if isinstance(obj, (list | tuple | set)):
        return [_json_sanitize(v) for v in obj]

    return str(obj)


class AuditlogRule(models.Model):
    _inherit = "auditlog.rule"

    def _next_ids(self, seq_name: str, count: int) -> list[int]:
        if count <= 0:
            return []
        self.env.cr.execute(
            "SELECT nextval(%s::regclass) FROM generate_series(1, %s)",
            (seq_name, count),
        )
        return [row[0] for row in self.env.cr.fetchall()]

    def _get_rule_settings(self, model_id):
        """Return rule settings for given model.

        Computes:
          - Union of excluded field names
          - Whether record capture is enabled

        Result is cached on registry pool to avoid repeated DB lookups.

        :param model_id: ir.model record ID
        :type model_id: int
        :return: (excluded_fields_set, capture_record_flag)
        :rtype: Tuple[Set[str], bool]
        """
        if not hasattr(self.pool, "_auditlog_clickhouse_write_rule_cache"):
            self.pool._auditlog_clickhouse_write_rule_cache = {}
        cache = self.pool._auditlog_clickhouse_write_rule_cache

        rules = self.sudo().filtered(lambda r: r.model_id.id == model_id)
        if not rules:
            domain = [("model_id", "=", model_id)]
            if "state" in self._fields:
                domain.append(("state", "=", "subscribed"))
            rules = self.sudo().search(domain)

        stamp = tuple(
            (
                rule.id,
                bool(rule.capture_record),
                tuple(sorted(rule.fields_to_exclude_ids.ids)),
                rule.write_date or rule.create_date,
            )
            for rule in rules.sorted("id")
        )
        key = (model_id, stamp)
        if key in cache:
            return cache[key]

        excluded: set[str] = set(FIELDS_BLACKLIST)
        capture_record = False

        if len(rules) > 1:
            _logger.warning(
                "auditlog_clickhouse_write: multiple rules found for model_id=%s "
                "(rules=%s); using union of excluded fields and any(capture_record).",
                model_id,
                rules.ids,
            )
        for rule in rules:
            excluded |= set(rule.fields_to_exclude_ids.mapped("name"))
            capture_record = capture_record or bool(rule.capture_record)

        cache[key] = (excluded, capture_record)
        return cache[key]

    def _serialize_http_session(self, session_id):
        """Serialize auditlog.http.session for ClickHouse buffering.

        :param session_id: HTTP session record ID
        :type session_id: Optional[int]
        :return: Serialized HTTP session payload or None
        :rtype: Optional[_PayloadHttpSession]
        """
        if not session_id:
            return None
        return (
            self.env["auditlog.http.session"].sudo().get_clickhouse_payload(session_id)
        )

    def _serialize_http_request(self, request_id):
        """Serialize auditlog.http.request for ClickHouse buffering.

        :param request_id: HTTP request record ID
        :type request_id: Optional[int]
        :return: Serialized HTTP request payload or None
        :rtype: Optional[_PayloadHttpRequest]
        """
        if not request_id:
            return None
        return (
            self.env["auditlog.http.request"].sudo().get_clickhouse_payload(request_id)
        )

    def _get_audit_model_id(self, res_model):
        """Resolve ir.model ID for given model name.

        Prefers auditlog in-memory cache, falls back to ir.model lookup.

        :param res_model: Technical model name (e.g. "res.partner")
        :type res_model: str
        :return: ir.model record ID
        :rtype: int
        """
        model_id = getattr(self.pool, "_auditlog_model_cache", {}).get(res_model)
        if model_id:
            return int(model_id)
        return int(self.env["ir.model"].sudo()._get(res_model).id)

    def _dump_payload_json(self, payload):
        """Sanitize payload for storage in fields.Json column.

        :param payload: Raw payload dictionary
        :type payload: Dict[str, Any]
        :return: JSON-serializable payload
        :rtype: Dict[str, Any]
        """
        return _json_sanitize(payload)

    def _get_http_ids(self):
        """Return current auditlog HTTP identifiers (same as base auditlog).

        :return: (http_request_id, http_session_id)
        :rtype: Tuple[Optional[int], Optional[int]]
        """
        http_request_id = (
            self.env["auditlog.http.request"].current_http_request() or None
        )
        http_session_id = (
            self.env["auditlog.http.session"].current_http_session() or None
        )
        return http_request_id, http_session_id

    def _build_base_log(
        self,
        *,
        uid,
        method,
        model_id,
        now_iso,
        log_type,
    ):
        """Build base log mapping shared across payloads.

        :param uid: User ID performing operation
        :type uid: int
        :param method: ORM method name
        :type method: str
        :param model_id: ir.model record ID
        :type model_id: int
        :param now_iso: UTC ISO timestamp with milliseconds
        :type now_iso: str
        :param log_type: Audit log type (from rule/additional values)
        :type log_type: Any
        :return: Base log dict
        :rtype: Dict[str, Any]
        """
        model_rec = self.env["ir.model"].sudo().browse(model_id)
        http_request_id, http_session_id = self._get_http_ids()

        return {
            "model_id": int(model_id),
            "model_name": model_rec.name,
            "model_model": model_rec.model,
            "user_id": int(uid),
            "method": method,
            "http_request_id": http_request_id,
            "http_session_id": http_session_id,
            "log_type": log_type,
            "create_date": now_iso,
            "create_uid": int(uid),
            "write_date": None,
            "write_uid": None,
        }

    def _get_buffer_model(self):
        """Return auditlog.log.buffer model used to store payloads.

        :return: auditlog.log.buffer model recordset (sudo + tracking_disable)
        :rtype: odoo.models.BaseModel
        """
        return (
            self.env["auditlog.log.buffer"].sudo().with_context(tracking_disable=True)
        )

    def _buffer_export_data_payload(
        self,
        *,
        buffer_model,
        base_log,
        res_model,
        res_ids,
        started,
    ):
        """Store export_data payload (no lines) into the buffer.

        :param buffer_model: auditlog.log.buffer model recordset
        :type buffer_model: odoo.models.BaseModel
        :param base_log: Base log mapping
        :type base_log: Dict[str, Any]
        :param res_model: Model technical name
        :type res_model: str
        :param res_ids: Record IDs affected
        :type res_ids: Sequence[int]
        :param started: monotonic() timestamp when create_logs started
        :type started: float
        """
        log_id = int(self._next_ids("auditlog_log_id_seq", 1)[0])
        payload: _Payload = {
            "log": {
                "id": log_id,
                "name": res_model,
                "res_id": None,
                "res_ids": str(list(res_ids)),
                **base_log,
            },
            "lines": [],
            **self._build_http_related_payload(base_log),
        }
        buffer_model.create([{"payload_json": self._dump_payload_json(payload)}])
        _logger.debug(
            "auditlog_clickhouse_write: create_logs end export_data (elapsed=%.3fs)",
            time.monotonic() - started,
        )

    def _select_line_builder_and_sources(
        self,
        *,
        method,
        include_lines_on_unlink,
        old_values,
        new_values,
    ):
        """Select line builder callback and value sources based on method.

        :param method: ORM method name
        :type method: str
        :param include_lines_on_unlink: Whether unlink should include lines
        :type include_lines_on_unlink: bool
        :param old_values: Values before change
        :type old_values: Mapping[int, Mapping[str, Any]]
        :param new_values: Values after change
        :type new_values: Mapping[int, Mapping[str, Any]]
        :return: (line_builder, values_src)
        :rtype: Tuple[Optional[Callable], Tuple]
        """
        if method == "create":
            return self._prepare_log_line_vals_on_create, (new_values,)
        if method == "read":
            return self._prepare_log_line_vals_on_read, (old_values,)
        if method == "write":
            return self._prepare_log_line_vals_on_write, (old_values, new_values)
        if include_lines_on_unlink:
            return self._prepare_log_line_vals_on_read, (old_values,)
        return None, ()

    @staticmethod
    def _fields_list_for_method(
        *,
        method,
        include_lines_on_unlink,
        diff: DictDiffer,
        old_values,
        res_id,
    ):
        """Return list of fields to build lines for given method.

        :param method: ORM method name
        :type method: str
        :param include_lines_on_unlink: Whether unlink should include lines
        :type include_lines_on_unlink: bool
        :param diff: DictDiffer for old/new values
        :type diff: DictDiffer
        :param old_values: Old values mapping
        :type old_values: Mapping[int, Mapping[str, Any]]
        :param res_id: Current record ID
        :type res_id: int
        :return: Iterable of field names
        :rtype: Any
        """
        if method == "create":
            return diff.added()
        if method == "read" or include_lines_on_unlink:
            return old_values.get(res_id, EMPTY_DICT).keys()
        if method == "write":
            return diff.changed()
        return ()

    def _build_payloads_for_records(
        self,
        *,
        uid,
        res_model,
        res_ids,
        method,
        model_id,
        model_rs,
        log_type,
        now_iso,
        base_log,
        fields_to_exclude_set,
        old_values,
        new_values,
        line_builder,
        values_src,
        include_lines_on_unlink,
    ):
        """Build buffered payload structures for each processed record.

        Each returned item contains:
          - log payload
          - line payloads
          - related HTTP payloads (session/request)

        :param uid: User ID performing operation.
        :type uid: int
        :param res_model: Model technical name.
        :type res_model: str
        :param res_ids: Record IDs affected.
        :type res_ids: Sequence[int]
        :param method: ORM method name.
        :type method: str
        :param model_id: ir.model record ID.
        :type model_id: int
        :param model_rs: Target model recordset.
        :type model_rs: odoo.models.BaseModel
        :param log_type: Audit log type.
        :type log_type: Any
        :param now_iso: UTC ISO timestamp with milliseconds.
        :type now_iso: str
        :param base_log: Base log mapping.
        :type base_log: Dict[str, Any]
        :param fields_to_exclude_set: Field names excluded from logging.
        :type fields_to_exclude_set: Set[str]
        :param old_values: Values before change.
        :type old_values: Mapping[int, Mapping[str, Any]]
        :param new_values: Values after change.
        :type new_values: Mapping[int, Mapping[str, Any]]
        :param line_builder: Callback to build line values.
        :type line_builder: Optional[Callable]
        :param values_src: Source value mappings for line building.
        :type values_src: Tuple
        :param include_lines_on_unlink: Whether unlink should include lines.
        :type include_lines_on_unlink: bool
        :return: Tuple of payload tuples and total line count.
        :rtype: Tuple[
            List[Tuple[_PayloadLog, List[_PayloadLine], Dict[str, Any]]],
            int,
        ]
        """
        log_ids = self._next_ids("auditlog_log_id_seq", len(res_ids))
        payloads: list[tuple[_PayloadLog, list[_PayloadLine], dict[str, Any]]] = []
        total_lines = 0

        for idx, res_id in enumerate(res_ids):
            log_id = int(log_ids[idx])
            record = model_rs.browse(res_id)

            log: _PayloadLog = {
                "id": log_id,
                "name": record.display_name,
                "res_id": int(res_id),
                "res_ids": None,
                **base_log,
            }

            diff = DictDiffer(
                dict(new_values.get(res_id, EMPTY_DICT)),
                dict(old_values.get(res_id, EMPTY_DICT)),
            )

            fields_list = self._fields_list_for_method(
                method=method,
                include_lines_on_unlink=include_lines_on_unlink,
                diff=diff,
                old_values=old_values,
                res_id=res_id,
            )

            lines: list[_PayloadLine] = []
            if line_builder:
                one_source = method in ("create", "read") or include_lines_on_unlink
                log_ctx = {"res_id": res_id, "model_id": model_id, "log_type": log_type}

                for field_name in fields_list:
                    if field_name in fields_to_exclude_set:
                        continue
                    field = self._get_field(model_id, field_name)
                    if not field:
                        continue

                    if one_source:
                        vals = line_builder(log_ctx, field, values_src[0])
                    else:
                        vals = line_builder(
                            log_ctx, field, values_src[0], values_src[1]
                        )

                    lines.append(
                        {
                            "id": 0,
                            "log_id": log_id,
                            "field_id": int(field["id"]),
                            "field_name": field.get("name"),
                            "field_description": field.get("field_description"),
                            "old_value": vals.get("old_value"),
                            "new_value": vals.get("new_value"),
                            "old_value_text": vals.get("old_value_text"),
                            "new_value_text": vals.get("new_value_text"),
                            "create_date": now_iso,
                            "create_uid": int(uid),
                            "write_date": None,
                            "write_uid": None,
                        }
                    )

            http_related = self._build_http_related_payload(log)
            payloads.append((log, lines, http_related))
            total_lines += len(lines)

        return payloads, total_lines

    def _build_buffer_vals_from_payloads(
        self,
        *,
        payloads,
        total_lines,
        method,
    ):
        """Assign line IDs and build buffer create vals.

        Line identifiers are allocated in one batch and injected into line payloads
        before serializing the final JSON stored in ``auditlog.log.buffer``.

        :param payloads: List of ``(log, lines, http_related)`` payload tuples.
        :type payloads: List[Tuple[_PayloadLog, List[_PayloadLine], Dict[str, Any]]]
        :param total_lines: Total number of line items across all payloads.
        :type total_lines: int
        :param method: ORM method name.
        :type method: str
        :return: Values list for ``auditlog.log.buffer.create()``.
        :rtype: List[Dict[str, Any]]
        """
        line_ids: list[int] = self._next_ids("auditlog_log_line_id_seq", total_lines)
        pos = 0

        buffer_vals_list: list[dict[str, Any]] = []
        for log, lines, http_related in payloads:
            for line in lines:
                line["id"] = int(line_ids[pos])
                pos += 1

            if method == "unlink" or lines:
                buffer_vals_list.append(
                    {
                        "payload_json": self._dump_payload_json(
                            {
                                "log": log,
                                "lines": lines,
                                **http_related,
                            }
                        )
                    }
                )

        return buffer_vals_list

    def _build_http_related_payload(self, base_log):
        """Build HTTP related payload blocks for current audit log entry.

        :param base_log: Base log mapping
        :type base_log: Dict[str, Any]
        :return: Mapping with serialized http_session/http_request payloads
        :rtype: Dict[str, Any]
        """
        http_session = self._serialize_http_session(base_log.get("http_session_id"))
        http_request = self._serialize_http_request(base_log.get("http_request_id"))
        return {
            "http_session": http_session,
            "http_request": http_request,
        }

    def create_logs(
        self,
        uid,
        res_model,
        res_ids,
        method,
        old_values=None,
        new_values=None,
        additional_log_values=None,
    ):
        """Override auditlog log creation to buffer payloads for ClickHouse.

        Behavior:
          - If no active ClickHouse config -> fallback to parent implementation.
          - Otherwise:
            - Build structured payload (log + lines)
            - Sanitize to JSON
            - Store in auditlog.log.buffer
          - Export to ClickHouse is performed asynchronously via queue_job.

        Supported methods:
          - create, read, write unlink export_data

        :param uid: User ID performing operation
        :type uid: int
        :param res_model: Model technical name
        :type res_model: str
        :param res_ids: Record IDs affected
        :type res_ids: Sequence[int]
        :param method: ORM method name
        :type method: str
        :param old_values: Values before change
        :type old_values: Optional[Mapping[int, Mapping[str, Any]]]
        :param new_values: Values after change
        :type new_values: Optional[Mapping[int, Mapping[str, Any]]]
        :param additional_log_values: Extra audit metadata
        :type additional_log_values: Optional[Mapping[str, Any]]
        """
        config = self.env["auditlog.clickhouse.config"].sudo().get_active_config()
        if not config:
            return super().create_logs(
                uid,
                res_model,
                res_ids,
                method,
                old_values=old_values,
                new_values=new_values,
                additional_log_values=additional_log_values,
            )

        started = time.monotonic()
        old_values = old_values or EMPTY_DICT
        new_values = new_values or EMPTY_DICT
        additional_log_values = dict(additional_log_values or {})
        log_type = additional_log_values.get("log_type")

        model_id = self._get_audit_model_id(res_model)
        model_rs = self.env[res_model]
        fields_to_exclude_set, capture_record = self._get_rule_settings(model_id)

        now_iso = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        base_log = self._build_base_log(
            uid=int(uid),
            method=method,
            model_id=int(model_id),
            now_iso=now_iso,
            log_type=log_type,
        )
        buffer_model = self._get_buffer_model()

        # export_data is special (no lines)
        if method == "export_data":
            self._buffer_export_data_payload(
                buffer_model=buffer_model,
                base_log=base_log,
                res_model=res_model,
                res_ids=res_ids,
                started=started,
            )
            return

        include_lines_on_unlink = method == "unlink" and capture_record
        line_builder, values_src = self._select_line_builder_and_sources(
            method=method,
            include_lines_on_unlink=include_lines_on_unlink,
            old_values=old_values,
            new_values=new_values,
        )

        payloads, total_lines = self._build_payloads_for_records(
            uid=int(uid),
            res_model=res_model,
            res_ids=res_ids,
            method=method,
            model_id=int(model_id),
            model_rs=model_rs,
            log_type=log_type,
            now_iso=now_iso,
            base_log=base_log,
            fields_to_exclude_set=fields_to_exclude_set,
            old_values=old_values,
            new_values=new_values,
            line_builder=line_builder,
            values_src=values_src,
            include_lines_on_unlink=include_lines_on_unlink,
        )

        buffer_vals_list = self._build_buffer_vals_from_payloads(
            payloads=payloads,
            total_lines=total_lines,
            method=method,
        )

        if buffer_vals_list:
            buffer_model.create(buffer_vals_list)

        _logger.debug(
            "auditlog_clickhouse_write: create_logs end (model=%s method=%s res_ids=%s "
            "payloads=%s lines=%s elapsed=%.3fs)",
            res_model,
            method,
            len(res_ids),
            len(buffer_vals_list),
            total_lines,
            time.monotonic() - started,
        )
