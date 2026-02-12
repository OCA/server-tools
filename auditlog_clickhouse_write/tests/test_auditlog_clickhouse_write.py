from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.queue_job.exception import RetryableJobError

from .common import AuditLogClickhouseCommon, DummyClickHouseClient


@tagged("-at_install", "post_install")
class TestAuditlogClickhouseBuffer(AuditLogClickhouseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.groups_model_id = cls.env.ref("base.model_res_groups").id

        # Rule for groups: full logging
        cls.groups_rule = cls.create_rule(
            {
                "name": "testrule groups clickhouse",
                "model_id": cls.groups_model_id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_export_data": True,
                "log_type": "full",
                "capture_record": False,
            }
        )

        # Active config to enable buffering
        cls.config = cls.create_config(is_active=True)

    def setUp(self):
        super().setUp()
        self.groups_rule.subscribe()

    def test_01_create_writes_to_buffer_not_auditlog_tables(self):
        buf = self.env["auditlog.log.buffer"].sudo()
        log_model = self.env["auditlog.log"]

        start_buf = buf.search_count([])
        start_logs = log_model.search_count([("model_id", "=", self.groups_model_id)])

        group = (
            self.env["res.groups"]
            .with_context(tracking_disable=True)
            .create({"name": "ch_test_group_1"})
        )

        self.assertEqual(
            log_model.search_count([("model_id", "=", self.groups_model_id)])
            - start_logs,
            0,
            "auditlog.log must NOT be written by auditlog_clickhouse_write",
        )
        self.assertEqual(buf.search_count([]) - start_buf, 1)

        payload = buf.search([], order="id desc", limit=1).payload_json
        self.assertEqual(payload["log"]["method"], "create")
        self.assertEqual(payload["log"]["model_id"], self.groups_model_id)
        self.assertEqual(payload["log"]["res_id"], group.id)

    def test_02_write_creates_lines(self):
        buf = self.env["auditlog.log.buffer"].sudo()
        start_buf = buf.search_count([])

        group = (
            self.env["res.groups"]
            .with_context(tracking_disable=True)
            .create({"name": "CH Group"})
        )
        group.with_context(tracking_disable=True).write({"name": "CH Group v2"})

        self.assertGreater(buf.search_count([]), start_buf)

        payload = buf.search([], order="id desc", limit=1).payload_json
        self.assertEqual(payload["log"]["method"], "write")
        self.assertEqual(payload["log"]["model_model"], "res.groups")

        field_names = {line.get("field_name") for line in payload["lines"]}
        self.assertIn("name", field_names)

    def test_03_export_data_creates_single_payload_no_lines(self):
        buf = self.env["auditlog.log.buffer"].sudo()
        start_buf = buf.search_count([])

        self.env["res.groups"].search([]).export_data(["name"])

        self.assertEqual(buf.search_count([]) - start_buf, 1)
        payload = buf.search([], order="id desc", limit=1).payload_json
        self.assertEqual(payload["log"]["method"], "export_data")
        self.assertEqual(payload["lines"], [])

    def test_04_unlink_is_logged(self):
        buf = self.env["auditlog.log.buffer"].sudo()
        start_buf = buf.search_count([])

        g = (
            self.env["res.groups"]
            .with_context(tracking_disable=True)
            .create({"name": "ch_test_group_unlink"})
        )
        g.unlink()

        self.assertGreater(buf.search_count([]), start_buf)
        payload = buf.search([], order="id desc", limit=1).payload_json
        self.assertEqual(payload["log"]["method"], "unlink")
        self.assertIsInstance(payload["lines"], list)


@tagged("-at_install", "post_install")
class TestAuditlogClickhouseQueueJobs(AuditLogClickhouseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model_id = cls.env.ref("base.model_res_partner").id
        cls.rule = cls.create_rule(
            {
                "name": "testrule partner clickhouse queue",
                "model_id": cls.partner_model_id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_type": "full",
            }
        )
        cls.config = cls.create_config(is_active=True)

    def setUp(self):
        super().setUp()
        self.rule.subscribe()

    def test_01_cron_enqueues_job_and_does_not_flush_inline(self):
        """
        Cron must only enqueue queue.job (no direct ClickHouse INSERTs here).
        """
        buf = self.env["auditlog.log.buffer"].sudo()
        job_model = self.env["queue.job"].sudo()

        partner = (
            self.env["res.partner"]
            .with_context(tracking_disable=True)
            .create({"name": "Cron Enqueue Test"})
        )
        partner.with_context(tracking_disable=True).write(
            {"name": "Cron Enqueue Test v2"}
        )

        self.assertGreater(buf.search_count([]), 0)

        start_jobs = job_model.search_count([])
        res = buf._cron_flush_to_clickhouse()  # uses config.queue_batch_size

        self.assertTrue(res)
        self.assertEqual(
            job_model.search_count([]) - start_jobs,
            1,
            "Cron must enqueue exactly one job",
        )

        job = job_model.search([], order="id desc", limit=1)
        self.assertEqual(job.model_name, "auditlog.log.buffer")
        self.assertEqual(job.method_name, "_job_flush_to_clickhouse")
        self.assertEqual(job.args[0], self.config.id)
        self.assertEqual(job.args[1], self.config.queue_batch_size)

        expected_channel = (
            self.config.queue_channel_id.complete_name
            if self.config.queue_channel_id
            else "root"
        )
        self.assertEqual(job.channel, expected_channel)

    def test_02_cron_skips_when_no_pending_buffers(self):
        buf = self.env["auditlog.log.buffer"].sudo()
        job_model = self.env["queue.job"].sudo()

        # Ensure no pending buffers
        buf.search([]).unlink()

        start_jobs = job_model.search_count([])
        res = buf._cron_flush_to_clickhouse()

        self.assertTrue(res)
        self.assertEqual(
            job_model.search_count([]) - start_jobs, 0, "No pending buffers -> no job"
        )

    def test_03_cron_skips_without_active_config(self):
        self.env["auditlog.clickhouse.config"].search([]).write({"is_active": False})

        buf = self.env["auditlog.log.buffer"].sudo()
        job_model = self.env["queue.job"].sudo()

        start_jobs = job_model.search_count([])
        rec = buf.create(
            {"payload_json": {"log": {}, "lines": []}, "state": buf.STATE_PENDING}
        )

        with mute_logger(
            "odoo.addons.auditlog_clickhouse_write.models.auditlog_log_buffer"
        ):
            res = buf._cron_flush_to_clickhouse()

        self.assertTrue(res)
        self.assertEqual(
            job_model.search_count([]) - start_jobs, 0, "No active config -> no job"
        )

        rec.invalidate_recordset()
        self.assertEqual(rec.state, buf.STATE_PENDING)
        self.assertFalse(rec.error_message)

    def test_04_job_flush_success_deletes_buffers_and_calls_insert(self):
        buf = self.env["auditlog.log.buffer"].sudo()

        partner = (
            self.env["res.partner"]
            .with_context(tracking_disable=True)
            .create({"name": "Job Flush OK"})
        )
        partner.with_context(tracking_disable=True).write({"name": "Job Flush OK v2"})

        self.assertGreater(buf.search_count([]), 0)

        with self._patched_clickhouse_client() as dummy:
            buf._job_flush_to_clickhouse(self.config.id, self.config.queue_batch_size)

        self.assertEqual(
            buf.search_count([]),
            0,
            "Buffers must be removed after successful job flush",
        )

        insert_calls = [
            q for (q, _params) in dummy.calls if "INSERT INTO" in (q or "").upper()
        ]
        self.assertTrue(insert_calls, "Job must insert into ClickHouse")

    def test_05_job_invalid_payload_marks_error_and_keeps_row(self):
        buf = self.env["auditlog.log.buffer"].sudo()

        # Invalid structure for payload_json (Json field accepts string,
        # but our code expects mapping with log/lines)
        rec = buf.create(
            {"payload_json": "NOT A JSON OBJECT", "state": buf.STATE_PENDING}
        )

        with mute_logger(
            "odoo.addons.auditlog_clickhouse_write.models.auditlog_log_buffer"
        ):
            buf._job_flush_to_clickhouse(self.config.id, batch_size=10)

        rec.invalidate_recordset()
        self.assertEqual(rec.state, buf.STATE_ERROR)
        self.assertTrue(rec.error_message)
        self.assertGreaterEqual(rec.attempt_count, 1)

    def test_06_retry_after_partial_insert_does_not_duplicate_log_rows(self):
        buf = self.env["auditlog.log.buffer"].sudo()
        buf.search([]).unlink()

        partner = (
            self.env["res.partner"]
            .with_context(tracking_disable=True)
            .create({"name": "Partial insert"})
        )
        partner.with_context(tracking_disable=True).write({"name": "Partial insert v2"})

        pending = buf.search([("state", "=", buf.STATE_PENDING)], order="id asc")
        valid_buffers, invalid_buffers, log_rows, line_rows = (
            buf._collect_rows_from_buffers(pending)
        )

        self.assertTrue(log_rows)
        self.assertTrue(line_rows)

        dummy = DummyClickHouseClient(raise_on_line_insert_once=True)

        # 1st try: expected failure -> mute ERROR traceback
        with mute_logger(
            "odoo.addons.auditlog_clickhouse_write.models.auditlog_log_buffer"
        ):
            with self.assertRaises(RetryableJobError):
                buf._insert_rows_to_clickhouse(
                    client=dummy,
                    config=self.config,
                    log_rows=log_rows,
                    line_rows=line_rows,
                    valid_buffers=valid_buffers,
                )

        # 2nd try: should pass
        buf._insert_rows_to_clickhouse(
            client=dummy,
            config=self.config,
            log_rows=log_rows,
            line_rows=line_rows,
            valid_buffers=valid_buffers,
        )

        log_inserts = [
            q
            for (q, _p) in dummy.calls
            if "INSERT INTO" in (q or "").upper()
            and "AUDITLOG_LOG" in (q or "").upper()
            and "AUDITLOG_LOG_LINE" not in (q or "").upper()
        ]
        self.assertEqual(
            len(log_inserts), 1, "Log rows must not be inserted twice on retry"
        )


@tagged("-at_install", "post_install")
class TestAuditlogClickhouseRuleCache(AuditLogClickhouseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model_id = cls.env.ref("base.model_res_partner").id
        cls.rule = cls.create_rule(
            {
                "name": "testrule cache invalidation",
                "model_id": cls.partner_model_id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_type": "full",
                "capture_record": False,
            }
        )

    def test_01_cache_updates_when_rule_changes_but_id_same(self):
        # isolate cache for this test
        if hasattr(self.env.registry, "_auditlog_clickhouse_write_rule_cache"):
            self.env.registry._auditlog_clickhouse_write_rule_cache = {}

        excluded_1, capture_1 = self.rule._get_rule_settings(self.partner_model_id)
        self.assertFalse(capture_1)

        # change rule with same id
        self.rule.write({"capture_record": True})
        self.rule.invalidate_recordset()

        excluded_2, capture_2 = self.rule._get_rule_settings(self.partner_model_id)
        self.assertTrue(capture_2)
