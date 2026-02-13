# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import json
from unittest import mock

from .common import JsonExportTestCase


class _MissingAttribute:
    """Descriptor that raises AttributeError when accessed (for hasattr checks)."""

    def __get__(self, obj, objtype=None):
        raise AttributeError("with_delay")


class TestJsonExportSchedule(JsonExportTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.schedule = cls.env["json.export.schedule"].create(
            {
                "name": "Test Schedule",
                "schema_id": cls.schema.id,
                "interval_number": 1,
                "interval_type": "hours",
                "destination_type": "attachment",
                "file_format": "json",
                "incremental": False,
            }
        )

    # -- Cron lifecycle tests --

    def test_create_schedule_creates_cron(self):
        """cron_id is populated after create."""
        self.assertTrue(self.schedule.cron_id)
        self.assertTrue(self.schedule.cron_id.active)

    def test_cron_interval_matches(self):
        """Cron interval matches schedule config."""
        cron = self.schedule.cron_id
        self.assertEqual(cron.interval_number, 1)
        self.assertEqual(cron.interval_type, "hours")

    def test_write_schedule_updates_cron(self):
        """Changing interval updates the cron."""
        self.schedule.write({"interval_number": 5, "interval_type": "days"})
        cron = self.schedule.cron_id
        self.assertEqual(cron.interval_number, 5)
        self.assertEqual(cron.interval_type, "days")

    def test_unlink_schedule_removes_cron(self):
        """Cron is deleted when schedule is deleted."""
        cron_id = self.schedule.cron_id.id
        self.schedule.unlink()
        self.assertFalse(self.env["ir.cron"].browse(cron_id).exists())

    def test_toggle_active_updates_cron(self):
        """Deactivating schedule deactivates the cron."""
        self.schedule.write({"active": False})
        self.assertFalse(self.schedule.cron_id.active)
        self.schedule.write({"active": True})
        self.assertTrue(self.schedule.cron_id.active)

    # -- Export execution tests --

    def test_run_export_attachment(self):
        """Creates ir.attachment with valid JSON content."""
        self.schedule._run_scheduled_export()
        attachments = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "json.export.schedule"),
                ("res_id", "=", self.schedule.id),
            ]
        )
        self.assertTrue(attachments)
        content = base64.b64decode(attachments[0].datas).decode("utf-8")
        data = json.loads(content)
        self.assertIsInstance(data, list)

    def test_run_export_jsonl_format(self):
        """JSONL format produces one JSON object per line."""
        self.schedule.write({"file_format": "jsonl"})
        self.schedule._run_scheduled_export()
        attachments = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "json.export.schedule"),
                ("res_id", "=", self.schedule.id),
                ("mimetype", "=", "application/x-ndjson"),
            ]
        )
        self.assertTrue(attachments)
        content = base64.b64decode(attachments[0].datas).decode("utf-8")
        lines = [line for line in content.strip().split("\n") if line]
        for line in lines:
            parsed = json.loads(line)
            self.assertIsInstance(parsed, dict)

    def test_run_export_incremental(self):
        """Incremental mode only exports records changed since last run."""
        # Set last_run_date to a point in the past
        past = "2000-01-01 00:00:00"
        self.schedule.write(
            {
                "incremental": True,
                "last_run_date": past,
            }
        )
        self.schedule._run_scheduled_export()
        # All records should be newer than 2000-01-01
        self.assertEqual(self.schedule.last_run_status, "success")
        self.assertGreater(self.schedule.last_run_count, 0)

    def test_run_export_updates_last_run(self):
        """Updates last_run_date, last_run_status, last_run_count."""
        self.schedule._run_scheduled_export()
        self.assertTrue(self.schedule.last_run_date)
        self.assertEqual(self.schedule.last_run_status, "success")
        self.assertGreaterEqual(self.schedule.last_run_count, 0)
        self.assertFalse(self.schedule.last_run_error)

    def test_run_export_http_post(self):
        """HTTP POST delivery sends data to destination_url."""
        self.schedule.write(
            {
                "destination_type": "http_post",
                "destination_url": "https://example.com/receive",
            }
        )
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        with mock.patch("requests.post", return_value=mock_response) as mock_post:
            self.schedule._run_scheduled_export()
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            self.assertEqual(call_args[0][0], "https://example.com/receive")
        self.assertEqual(self.schedule.last_run_status, "success")

    def test_run_export_error_handling(self):
        """Sets last_run_status='error' on failure."""
        self.schedule.write(
            {
                "destination_type": "http_post",
                "destination_url": "https://example.com/fail",
            }
        )
        import requests as req

        with mock.patch(
            "requests.post",
            side_effect=req.ConnectionError("Connection refused"),
        ):
            self.schedule._run_scheduled_export()
        self.assertEqual(self.schedule.last_run_status, "error")
        self.assertTrue(self.schedule.last_run_error)

    def test_action_run_now(self):
        """Manual trigger works."""
        result = self.schedule.action_run_now()
        self.assertTrue(result)
        self.assertEqual(self.schedule.last_run_status, "success")

    def test_cron_run_export(self):
        """_cron_run_export entry point works for valid schedule."""
        self.env["json.export.schedule"]._cron_run_export(self.schedule.id)
        self.assertEqual(self.schedule.last_run_status, "success")

    def test_cron_run_export_invalid_id(self):
        """_cron_run_export silently skips non-existent schedule."""
        # Should not raise
        self.env["json.export.schedule"]._cron_run_export(99999)

    # -- Async export tests --

    def test_async_export_uses_with_delay(self):
        """When async_export=True and with_delay exists, it is called."""
        self.schedule.async_export = True
        mock_delayed = mock.MagicMock()
        with mock.patch.object(
            type(self.schedule), "with_delay", create=True, return_value=mock_delayed
        ):
            self.env["json.export.schedule"]._cron_run_export(self.schedule.id)
            mock_delayed._run_scheduled_export.assert_called_once()

    def test_async_export_fallback_sync(self):
        """When async_export=True but with_delay is absent, falls back to sync."""
        self.schedule.async_export = True
        # Mock with_delay to raise AttributeError to simulate non-queue_job install
        schedule_class = type(self.schedule)
        with mock.patch.object(schedule_class, "with_delay", new=_MissingAttribute()):
            self.env["json.export.schedule"]._cron_run_export(self.schedule.id)
            self.assertEqual(self.schedule.last_run_status, "success")
