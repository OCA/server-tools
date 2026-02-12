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

    def execute(self, query, params=None):
        self.calls.append((query, params))
        q = (query or "").strip()
        q_up = q.upper()

        if q_up.startswith("SELECT 1"):
            return [(1,)]

        if q_up.startswith("SELECT ID FROM") and "AUDITLOG_LOG" in q_up:
            wanted = self._parse_in_ids(q)
            existing = sorted(self.log_ids.intersection(wanted))
            return [(x,) for x in existing]

        if self.raise_on_insert and "INSERT INTO" in q_up:
            raise Exception("Simulated ClickHouse insert error")

        if "INSERT INTO" in q_up and "AUDITLOG_LOG_LINE" in q_up:
            if self.raise_on_line_insert_once and not self._line_failed_once:
                self._line_failed_once = True
                raise Exception("Simulated ClickHouse line insert error")
            return []

        if (
            "INSERT INTO" in q_up
            and "AUDITLOG_LOG" in q_up
            and "AUDITLOG_LOG_LINE" not in q_up
        ):
            # collect inserted ids (1st tuple element)
            if params:
                for row in params:
                    self.log_ids.add(row[0])
            return []

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
