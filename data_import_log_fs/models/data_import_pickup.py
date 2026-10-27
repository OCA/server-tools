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
    _inherit = ["mail.thread"]
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
        default="processing",
        help="Directory a file is held in while it is being imported. Leave "
        "empty to leave it in the incoming directory, where its open import log "
        "keeps a later scan from taking it again.",
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
    scan_error = fields.Text(
        "Last Scan Error",
        readonly=True,
        copy=False,
        help="Why the latest scan failed. Cleared by a scan that succeeds.",
    )
    scan_failed_since = fields.Datetime(
        readonly=True,
        copy=False,
        help="When the scans of this pick-up started failing.",
    )

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

    def _held_path(self, name):
        """Return where a file is while it is being imported."""
        self.ensure_one()
        return f"{self.path_processing or self.path_in}/{name}"

    def _is_being_imported(self, name):
        """Return whether an import of a file of this name is still running."""
        self.ensure_one()
        if self.path_processing:
            # Taking it in would overwrite the copy the running import holds,
            # and both logs would then claim one path.
            return self.backend_id.fs.exists(self._held_path(name))
        # The file never left the incoming directory, so only its log tells.
        return bool(
            self.env["data.import.log"].search_count(
                [
                    ("pickup_id", "=", self.id),
                    ("file_name", "=", name),
                    ("state", "in", ["pending", "processing"]),
                ],
                limit=1,
            )
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
        if self._is_being_imported(name):
            _logger.info("%s is still being imported, left in place.", source)
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
        if self.path_processing:
            fs.mv(source, self._held_path(name))
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
            except Exception as error:
                # The next pick-up must start from a sound transaction.
                if not modules.module.current_test:
                    self.env.cr.rollback()
                _logger.exception("Pick-up %s could not be scanned.", pickup.name)
                pickup._scan_failed(error)
            else:
                if pickup.scan_failed_since:
                    pickup._scan_recovered()
        return logs

    def _scan_failed(self, error):
        """Record a failed scan, and tell the job managers when it is the first.

        A storage that cannot be reached fails every run until it is back, so
        only the first failure is announced, not each run of the cron.
        """
        self.ensure_one()
        values = {"scan_error": str(error) or repr(error)}
        first = not self.scan_failed_since
        if first:
            values["scan_failed_since"] = fields.Datetime.now()
        self.write(values)
        if first:
            group = self.env.ref("queue_job.group_queue_job_manager")
            users = self.env["res.users"].search([("group_ids", "=", group.id)])
            self.message_subscribe(partner_ids=users.partner_id.ids)
            self.message_post(
                body=self.env._(
                    "Pick-up %(name)s could not be scanned: %(error)s",
                    name=self.name,
                    error=values["scan_error"],
                ),
                subtype_xmlid="mail.mt_comment",
            )
        self._commit_scan_state()

    def _scan_recovered(self):
        """Clear a failure once the pick-up is scanned again."""
        self.ensure_one()
        self.message_post(
            body=self.env._(
                "Pick-up %(name)s is scanned again, after failing since %(since)s.",
                name=self.name,
                since=fields.Datetime.to_string(self.scan_failed_since),
            ),
            subtype_xmlid="mail.mt_note",
        )
        self.write({"scan_error": False, "scan_failed_since": False})
        self._commit_scan_state()

    def _commit_scan_state(self):
        # A later pick-up that fails rolls back, which must not take this
        # record with it.
        if not modules.module.current_test:
            # pylint: disable=invalid-commit
            self.env.cr.commit()

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
