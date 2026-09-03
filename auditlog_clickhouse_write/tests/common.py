import contextlib
import re
from unittest.mock import patch

from odoo.addons.auditlog.tests.common import AuditLogRuleCommon


class DummyClickHouseClient:
    """Tiny fake clickhouse client collecting execute() calls."""

    def __init__(
        self, *, raise_on_insert: bool = False, raise_on_line_insert_once: bool = False
    ):
        self.raise_on_insert = raise_on_insert
        self.raise_on_line_insert_once = raise_on_line_insert_once
        self._line_failed_once = False

        self.calls = []  # list[(query, params)]
        self.log_ids = set()
        self.line_ids = set()
        self.http_session_ids = set()
        self.http_request_ids = set()

    def _parse_in_ids(self, query):
        m = re.search(r"\bIN\s*\(([^)]*)\)", query, flags=re.IGNORECASE)
        if not m:
            return set()
        raw = m.group(1).strip()
        if not raw:
            return set()
        ids = set()
        for part in raw.split(","):
            p = part.strip().strip("'")
            if not p:
                continue
            # tests use ints
            try:
                ids.add(int(p))
            except ValueError:
                ids.add(p)
        return ids

    @staticmethod
    def _is_select_ids_query(q_up, table_name):
        return q_up.startswith("SELECT ID FROM") and table_name in q_up

    @staticmethod
    def _is_insert_query(q_up, table_name):
        return "INSERT INTO" in q_up and table_name in q_up

    def _select_existing_ids(self, query, stored_ids):
        wanted = self._parse_in_ids(query)
        existing = sorted(stored_ids.intersection(wanted))
        return [(row_id,) for row_id in existing]

    @staticmethod
    def _collect_inserted_ids(params, target_set):
        if not params:
            return
        for row in params:
            target_set.add(row[0])

    def _handle_select(self, q, q_up):
        if q_up.startswith("SELECT 1"):
            return [(1,)]

        if self._is_select_ids_query(q_up, "AUDITLOG_HTTP_SESSION"):
            return self._select_existing_ids(q, self.http_session_ids)

        if self._is_select_ids_query(q_up, "AUDITLOG_HTTP_REQUEST"):
            return self._select_existing_ids(q, self.http_request_ids)

        if self._is_select_ids_query(q_up, "AUDITLOG_LOG_LINE"):
            return self._select_existing_ids(q, self.line_ids)

        if (
            self._is_select_ids_query(q_up, "AUDITLOG_LOG")
            and "AUDITLOG_LOG_LINE" not in q_up
        ):
            return self._select_existing_ids(q, self.log_ids)

        return None

    def _handle_insert(self, q_up, params):
        if self.raise_on_insert and "INSERT INTO" in q_up:
            raise Exception("Simulated ClickHouse insert error")

        if self._is_insert_query(q_up, "AUDITLOG_LOG_LINE"):
            if self.raise_on_line_insert_once and not self._line_failed_once:
                self._line_failed_once = True
                raise Exception("Simulated ClickHouse line insert error")
            self._collect_inserted_ids(params, self.line_ids)
            return []

        if self._is_insert_query(q_up, "AUDITLOG_HTTP_SESSION"):
            self._collect_inserted_ids(params, self.http_session_ids)
            return []

        if self._is_insert_query(q_up, "AUDITLOG_HTTP_REQUEST"):
            self._collect_inserted_ids(params, self.http_request_ids)
            return []

        if (
            self._is_insert_query(q_up, "AUDITLOG_LOG")
            and "AUDITLOG_LOG_LINE" not in q_up
        ):
            self._collect_inserted_ids(params, self.log_ids)
            return []

        return None

    def execute(self, query, params=None):
        self.calls.append((query, params))
        q = (query or "").strip()
        q_up = q.upper()

        select_result = self._handle_select(q, q_up)
        if select_result is not None:
            return select_result

        insert_result = self._handle_insert(q_up, params)
        if insert_result is not None:
            return insert_result

        return []


class AuditLogClickhouseCommon(AuditLogRuleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._cleanup_clickhouse_test_data()

    @classmethod
    def tearDownClass(cls):
        try:
            cls._cleanup_clickhouse_test_data()
        finally:
            super().tearDownClass()

    @classmethod
    def _cleanup_clickhouse_test_data(cls):
        """Ensure clean state for configs and buffer across suites."""
        cls.env["auditlog.clickhouse.config"].sudo().search([]).write(
            {"is_active": False}
        )
        cls.env["auditlog.log.buffer"].sudo().search([]).unlink()

    @classmethod
    def create_config(cls, **vals):
        """Create ClickHouse config with minimal defaults for tests."""
        defaults = {
            "host": "localhost",
            "port": 9000,
            "database": "db",
            "user": "user",
            "password": "pass",
            "is_active": False,
        }
        defaults.update(vals)
        return (
            cls.env["auditlog.clickhouse.config"]
            .with_context(tracking_disable=True)
            .create(defaults)
        )

    @contextlib.contextmanager
    def _patched_clickhouse_client(self, *, raise_on_insert: bool = False):
        """Patch ClickHouse client getter so tests don't require real ClickHouse."""
        dummy = DummyClickHouseClient(raise_on_insert=raise_on_insert)
        target = (
            "odoo.addons.auditlog_clickhouse_write.models."
            "auditlog_clickhouse_config.get_clickhouse_client"
        )
        with patch(target, autospec=True, return_value=dummy):
            yield dummy

    def _parse_payloads(self):
        """Return list of decoded payload dicts from buffer (oldest first)."""
        buf = self.env["auditlog.log.buffer"].sudo().search([], order="id asc")
        return [rec.payload_json for rec in buf]
