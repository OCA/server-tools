# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

DEFAULT_RETENTION_DAYS = 90
DEFAULT_CHUNK_SIZE = 1000


class JsonExportAutovacuum(models.TransientModel):
    _name = "json.export.autovacuum"
    _description = "JSON Export Log Autovacuum"

    @api.model
    def autovacuum(self, days=None, chunk_size=None):
        """Delete json.export.log records older than *days*.

        :param days: retention period in days; falls back to the system
            parameter ``json_export_engine.log_retention_days`` (default 90).
        :param chunk_size: maximum records to delete per batch (default 1000).
        """
        if days is None:
            days = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "json_export_engine.log_retention_days",
                    DEFAULT_RETENTION_DAYS,
                )
            )
        if chunk_size is None:
            chunk_size = DEFAULT_CHUNK_SIZE

        cutoff = fields.Datetime.subtract(fields.Datetime.now(), days=days)
        LogModel = self.env["json.export.log"].sudo()

        total_deleted = 0
        while True:
            logs = LogModel.search(
                [("create_date", "<", cutoff)],
                limit=chunk_size,
            )
            if not logs:
                break
            count = len(logs)
            logs.with_context(norecompute=True).unlink()
            total_deleted += count
            if count < chunk_size:
                break

        _logger.info(
            "JSON Export autovacuum: deleted %d log entries older than %d days",
            total_deleted,
            days,
        )
        return total_deleted
