# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import base64
import logging
import re

from odoo import api, fields, models, modules

_logger = logging.getLogger(__name__)

# A file still being written is named so by convention, and is not ours yet.
INCOMPLETE_SUFFIX = ".tmp"
# Fixed, because it has to mean the same thing in every process that takes it.
SCAN_LOCK_KEY = 84213310


class DataImportPickup(models.Model):
    _name = "data.import.pickup"
    _description = "Data Import Pick-up"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(
        default=10,
        help="Order the pick-ups are scanned in, for feeds whose files depend "
        "on one another.",
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )
    backend_id = fields.Many2one(
        "fs.storage", string="Storage", required=True, ondelete="restrict"
    )
    path_in = fields.Char(
        "Incoming Path",
        required=True,
        default="in",
        help="Directory the files are picked up from, relative to the storage.",
    )
    path_processing = fields.Char(
        "Processing Path",
        required=True,
        default="processing",
        help="Directory a file is held in while it is being imported.",
    )
    path_done = fields.Char("Done Path", required=True, default="done")
    path_error = fields.Char(
        "Error Path",
        required=True,
        default="error",
        help="Directory the files reporting rejected units are written to.",
    )
    filename_pattern = fields.Char(
        default=r".*\.csv$",
        help="Only the files whose name matches this regular expression are picked up.",
    )
    file_format = fields.Selection(
        [("csv", "CSV"), ("xlsx", "Excel")], required=True, default="csv"
    )
    encoding = fields.Char(default="utf-8")
    column_names = fields.Text(
        help="Names to give the columns, one per line, in the order they appear "
        "in the files of this pick-up. Leave empty to take them from the "
        "header row.",
    )
    has_header = fields.Boolean(
        default=True,
        help="Whether the first row of the files holds the column names.",
    )
    log_ids = fields.One2many("data.import.log", "pickup_id", string="Import Logs")

    _name_uniq = models.Constraint("UNIQUE (name)", "A pick-up name must be unique.")

    def _matching_names(self, names):
        """Return the names to take in, in a stable order."""
        self.ensure_one()
        pattern = re.compile(self.filename_pattern or ".*")
        return sorted(
            name
            for name in names
            if not name.endswith(INCOMPLETE_SUFFIX) and pattern.match(name)
        )

    def _take_in(self, name):
        """Create the log for one file and hold the file while it is imported.

        Returns the log, or an empty recordset when there is nothing to import:
        a sender resends a whole file to correct a unit of it, so an identical
        file is skipped only when its earlier import succeeded whole.
        """
        self.ensure_one()
        fs = self.backend_id.fs
        source = f"{self.path_in}/{name}"
        held = f"{self.path_processing}/{name}"
        if fs.exists(held):
            # Taking it in would overwrite the copy the running import holds,
            # and both logs would then claim one path.
            _logger.info("%s is still being imported, %s left in place.", held, source)
            return self.env["data.import.log"]
        with fs.open(source, "rb") as fh:
            content = fh.read()
        log_model = self.env["data.import.log"]
        content_hash = log_model._content_hash(content)
        if log_model.search_count(
            [
                ("pickup_id", "=", self.id),
                ("file_name", "=", name),
                ("content_hash", "=", content_hash),
                ("state", "=", "done"),
            ],
            limit=1,
        ):
            _logger.info("%s was imported in full already, left in place.", source)
            return log_model
        attachment = self.env["ir.attachment"].create(
            {"name": name, "datas": base64.b64encode(content)}
        )
        log = log_model.create(
            {
                "pickup_id": self.id,
                "attachment_id": attachment.id,
                "content_hash": content_hash,
                "file_format": self.file_format,
                "encoding": self.encoding,
                "column_names": self.column_names,
                "has_header": self.has_header,
                "company_id": self.company_id.id,
            }
        )
        fs.mv(source, f"{self.path_processing}/{name}")
        return log

    def _scan_one(self, logs):
        """Take in every file waiting for this pick-up, and return the logs."""
        self.ensure_one()
        fs = self.backend_id.fs
        if not fs.exists(self.path_in):
            return logs
        names = [path.rsplit("/", 1)[-1] for path in fs.ls(self.path_in, detail=False)]
        for name in self._matching_names(names):
            log = self._take_in(name)
            if not log:
                continue
            logs |= log
            log._enqueue_parse()
            # Its source has already moved on the remote filesystem, which no
            # rollback undoes, so a later failure must not discard its log.
            if not modules.module.current_test:
                # pylint: disable=invalid-commit
                self.env.cr.commit()
        return logs

    def _scan(self):
        """Take in every file waiting for each pick-up.

        Pick-ups are separate feeds sharing a cron, so one that cannot be
        reached must not stop the others.
        """
        logs = self.env["data.import.log"]
        # Sorted here rather than relying on the caller: a recordset keeps the
        # order it was built in, and a feed whose files depend on one another
        # needs them taken in a known order.
        for pickup in self.sorted():
            try:
                logs = pickup._scan_one(logs)
            except Exception:
                # The next pick-up must start from a sound transaction.
                if not modules.module.current_test:
                    self.env.cr.rollback()
                _logger.exception("Pick-up %s could not be scanned.", pickup.name)
        return logs

    @api.model
    def _cron_scan(self):
        """Scan every pick-up, unless a previous run is still going.

        The lock is session-level because the scan commits per file, which
        would release a transaction-level one halfway through.
        """
        self.env.cr.execute("SELECT pg_try_advisory_lock(%s)", (SCAN_LOCK_KEY,))
        if not self.env.cr.fetchone()[0]:
            _logger.info("Another scan is running, skipped.")
            return
        try:
            # Configuration: a handful of records, all wanted.
            # pylint: disable=no-search-all
            self.search([])._scan()
        finally:
            self.env.cr.execute("SELECT pg_advisory_unlock(%s)", (SCAN_LOCK_KEY,))
