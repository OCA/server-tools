# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import json
import logging
import time

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class JsonExportSchedule(models.Model):
    _name = "json.export.schedule"
    _description = "JSON Export Schedule"
    _order = "name"

    name = fields.Char(required=True)
    schema_id = fields.Many2one(
        "json.export.schema",
        string="Export Schema",
        required=True,
        ondelete="cascade",
    )
    active = fields.Boolean(default=True)
    interval_number = fields.Integer(default=1, required=True)
    interval_type = fields.Selection(
        [
            ("minutes", "Minutes"),
            ("hours", "Hours"),
            ("days", "Days"),
            ("weeks", "Weeks"),
        ],
        default="hours",
        required=True,
    )
    cron_id = fields.Many2one(
        "ir.cron",
        string="Scheduled Action",
        readonly=True,
        ondelete="set null",
    )
    destination_type = fields.Selection(
        [
            ("attachment", "File Attachment"),
            ("http_post", "HTTP POST"),
        ],
        default="attachment",
        required=True,
    )
    destination_url = fields.Char(
        string="Destination URL",
        help="URL to POST the export data to (when destination type is HTTP POST).",
    )
    file_format = fields.Selection(
        [
            ("json", "JSON Array"),
            ("jsonl", "JSON Lines"),
        ],
        default="json",
        required=True,
    )
    incremental = fields.Boolean(
        default=True,
        help="Only export records modified since the last successful run.",
    )
    async_export = fields.Boolean(
        default=False,
        help="When enabled and queue_job is installed, "
        "export runs as a background job.",
    )
    last_run_date = fields.Datetime(readonly=True)
    last_run_status = fields.Selection(
        [("success", "Success"), ("error", "Error")],
        readonly=True,
    )
    last_run_count = fields.Integer(readonly=True)
    last_run_error = fields.Text(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.active:
                rec._create_or_update_cron()
        return records

    def write(self, vals):
        res = super().write(vals)
        cron_fields = {
            "active",
            "interval_number",
            "interval_type",
            "name",
            "schema_id",
        }
        if cron_fields & set(vals.keys()):
            for rec in self:
                rec._create_or_update_cron()
        return res

    def unlink(self):
        crons = self.mapped("cron_id")
        res = super().unlink()
        crons.sudo().unlink()
        return res

    def _create_or_update_cron(self):
        """Create or update the ir.cron record for this schedule."""
        self.ensure_one()
        cron_vals = {
            "name": f"JSON Export: {self.name}",
            "model_id": self.env["ir.model"]
            .sudo()
            .search([("model", "=", self._name)], limit=1)
            .id,
            "state": "code",
            "code": f"model._cron_run_export({self.id})",
            "interval_number": self.interval_number,
            "interval_type": self.interval_type,
            "active": self.active,
        }
        if self.cron_id:
            self.cron_id.sudo().write(cron_vals)
        else:
            cron = self.env["ir.cron"].sudo().create(cron_vals)
            self.cron_id = cron

    @api.model
    def _cron_run_export(self, schedule_id):
        """Entry point called by ir.cron."""
        schedule = self.browse(schedule_id)
        if schedule.exists() and schedule.active:
            if schedule.async_export and hasattr(schedule, "with_delay"):
                schedule.with_delay(
                    description=f"Scheduled Export: {schedule.name}",
                )._run_scheduled_export()
            else:
                schedule._run_scheduled_export()

    def _run_scheduled_export(self):
        """Execute the scheduled export."""
        self.ensure_one()
        start_time = time.time()
        schema = self.schema_id
        try:
            # Build extra domain for incremental export
            extra_domain = []
            if self.incremental and self.last_run_date:
                extra_domain = [("write_date", ">", self.last_run_date)]

            records = schema._get_records(
                no_limit=True,
                extra_domain=extra_domain,
            )
            data = schema._serialize_records(records)

            # Format output
            if self.file_format == "jsonl":
                content = "\n".join(
                    json.dumps(item, ensure_ascii=False) for item in data
                )
                mimetype = "application/x-ndjson"
                ext = "jsonl"
            else:
                content = json.dumps(data, indent=2, ensure_ascii=False)
                mimetype = "application/json"
                ext = "json"

            # Deliver
            if self.destination_type == "attachment":
                filename = (
                    f"scheduled_{schema.model_name.replace('.', '_')}_"
                    f"{fields.Datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                )
                self.env["ir.attachment"].create(
                    {
                        "name": filename,
                        "type": "binary",
                        "datas": base64.b64encode(content.encode("utf-8")),
                        "mimetype": mimetype,
                        "res_model": self._name,
                        "res_id": self.id,
                    }
                )
            elif self.destination_type == "http_post":
                if not self.destination_url:
                    raise UserError(
                        _("Destination URL is required for HTTP POST delivery.")
                    )
                resp = requests.post(
                    self.destination_url,
                    data=content,
                    headers={"Content-Type": mimetype},
                    timeout=120,
                )
                resp.raise_for_status()

            duration = int((time.time() - start_time) * 1000)
            self.write(
                {
                    "last_run_date": fields.Datetime.now(),
                    "last_run_status": "success",
                    "last_run_count": len(data),
                    "last_run_error": False,
                }
            )
            schema._create_log(
                "schedule",
                "success",
                len(data),
                duration,
                request_info=json.dumps(
                    {
                        "schedule": self.name,
                        "destination": self.destination_type,
                        "incremental": self.incremental,
                        "format": self.file_format,
                    }
                ),
            )
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.write(
                {
                    "last_run_date": fields.Datetime.now(),
                    "last_run_status": "error",
                    "last_run_count": 0,
                    "last_run_error": str(e),
                }
            )
            schema._create_log("schedule", "error", 0, duration, error_message=str(e))
            _logger.exception("Scheduled export '%s' failed", self.name)

    def action_run_now(self):
        """Manually trigger the scheduled export."""
        self.ensure_one()
        self._run_scheduled_export()
        return True
