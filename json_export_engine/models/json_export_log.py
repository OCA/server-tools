# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class JsonExportLog(models.Model):
    _name = "json.export.log"
    _description = "JSON Export Log"
    _order = "create_date desc"

    schema_id = fields.Many2one(
        "json.export.schema",
        string="Export Schema",
        required=True,
        ondelete="cascade",
        index=True,
    )
    log_type = fields.Selection(
        [
            ("api", "API Call"),
            ("webhook", "Webhook"),
            ("schedule", "Scheduled Export"),
            ("preview", "Preview"),
            ("manual", "Manual Export"),
        ],
        required=True,
        index=True,
    )
    status = fields.Selection(
        [("success", "Success"), ("error", "Error")],
        required=True,
    )
    records_count = fields.Integer(string="Records")
    duration_ms = fields.Integer(string="Duration (ms)")
    error_message = fields.Text()
    request_info = fields.Text(
        help="JSON with additional context about the request.",
    )
