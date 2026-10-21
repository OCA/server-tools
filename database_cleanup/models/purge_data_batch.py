# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""Purge orphaned data entries in batches.

``cleanup.purge.wizard.data`` builds one transient record per orphaned
``ir.model.data`` row and unlinks all of them in a single transaction. On big
databases this is very slow (and can fill up the disk with WAL files), because
the number of orphaned rows can be in the hundreds of thousands.

This wizard instead keeps only one progress line per model and deletes the
orphaned entries in batches, committing after each batch.
"""

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.sql import table_exists

from ..identifier_adapter import IdentifierAdapter

_logger = logging.getLogger(__name__)


class CleanupPurgeWizardDataBatchLine(models.TransientModel):
    _name = "cleanup.purge.wizard.data.batch.line"
    _description = "Purge data in batches: progress per model"
    _order = "sequence, id"

    wizard_id = fields.Many2one(
        "cleanup.purge.wizard.data.batch",
        "Wizard",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    sequence = fields.Integer(readonly=True)
    model = fields.Char(readonly=True)
    table_name = fields.Char(readonly=True)
    missing_model = fields.Boolean(
        readonly=True,
        help="The model is not available anymore: all its data entries are "
        "orphaned.",
    )
    orphan_count = fields.Integer(
        readonly=True, help="Number of orphaned entries found for this model."
    )
    purged_count = fields.Integer(readonly=True)
    remaining_count = fields.Integer(compute="_compute_remaining_count")
    last_id = fields.Integer(
        readonly=True,
        help="Highest data entry id already processed, used to resume the scan.",
    )
    done = fields.Boolean(readonly=True)

    @api.depends("orphan_count", "purged_count")
    def _compute_remaining_count(self):
        for line in self:
            line.remaining_count = max(line.orphan_count - line.purged_count, 0)


class CleanupPurgeWizardDataBatch(models.TransientModel):
    _name = "cleanup.purge.wizard.data.batch"
    _description = "Purge data entries in batches"

    batch_size = fields.Integer(
        default=1000,
        required=True,
        help="Number of data entries deleted and committed per batch. Use a "
        "smaller value if the database is slow or the transaction log grows "
        "too much.",
    )
    line_ids = fields.One2many(
        "cleanup.purge.wizard.data.batch.line",
        "wizard_id",
        "Progress per model",
        readonly=True,
    )
    orphan_count = fields.Integer(compute="_compute_progress")
    purged_count = fields.Integer(compute="_compute_progress")
    remaining_count = fields.Integer(compute="_compute_progress")
    progress = fields.Float(
        compute="_compute_progress", string="Progress (%)", readonly=True
    )
    done = fields.Boolean(compute="_compute_progress")
    logger = logging.getLogger("odoo.addons.database_cleanup")

    @api.constrains("batch_size")
    def _check_batch_size(self):
        for wizard in self:
            if wizard.batch_size < 1:
                raise ValidationError(_("The batch size must be at least 1."))

    @api.depends("line_ids.orphan_count", "line_ids.purged_count")
    def _compute_progress(self):
        for wizard in self:
            orphan_count = sum(wizard.line_ids.mapped("orphan_count"))
            purged_count = sum(wizard.line_ids.mapped("purged_count"))
            wizard.orphan_count = orphan_count
            wizard.purged_count = purged_count
            wizard.remaining_count = max(orphan_count - purged_count, 0)
            wizard.progress = (
                purged_count * 100.0 / orphan_count if orphan_count else 100.0
            )
            wizard.done = not wizard.remaining_count

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "line_ids" in fields_list:
            res["line_ids"] = self.find()
        return res

    @api.model
    def _count_orphans(self, model, table_name, missing_model):
        """Return the number of orphaned entries of ``model``."""
        if missing_model:
            # The model does not exist anymore: every entry is orphaned.
            self.env.cr.execute(
                "SELECT count(*) FROM ir_model_data WHERE model = %s", [model]
            )
        else:
            self.env.cr.execute(
                "SELECT count(*) FROM ir_model_data "
                "WHERE model = %s AND res_id IS NOT NULL AND NOT EXISTS ("
                "SELECT 1 FROM %s rel WHERE rel.id = ir_model_data.res_id)",
                [model, IdentifierAdapter(table_name)],
            )
        return self.env.cr.fetchone()[0]

    @api.model
    def _find_orphan_ids(self, line, limit):
        """Return up to ``limit`` orphaned data entry ids for a progress line,
        resuming after the last id already processed."""
        if line.missing_model:
            self.env.cr.execute(
                "SELECT id FROM ir_model_data "
                "WHERE model = %s AND id > %s ORDER BY id LIMIT %s",
                [line.model, line.last_id, limit],
            )
        else:
            self.env.cr.execute(
                "SELECT id FROM ir_model_data "
                "WHERE model = %s AND res_id IS NOT NULL AND NOT EXISTS ("
                "SELECT 1 FROM %s rel WHERE rel.id = ir_model_data.res_id) "
                "AND id > %s ORDER BY id LIMIT %s",
                [
                    line.model,
                    IdentifierAdapter(line.table_name),
                    line.last_id,
                    limit,
                ],
            )
        return [row[0] for row in self.env.cr.fetchall()]

    @api.model
    def find(self):
        """Scan ``ir_model_data`` and return one progress line per model
        having orphaned entries."""
        self.env.cr.execute(
            "SELECT DISTINCT model FROM ir_model_data "
            "WHERE model IS NOT NULL AND model != '' ORDER BY model"
        )
        models = [row[0] for row in self.env.cr.fetchall()]
        res = []
        sequence = 0
        for model in models:
            sequence += 10
            table_name = False
            missing_model = True
            if model in self.env and self.env[model]._table:
                table = self.env[model]._table
                if table_exists(self.env.cr, table):
                    table_name = table
                    missing_model = False
            orphan_count = self._count_orphans(model, table_name, missing_model)
            if not orphan_count:
                continue
            res.append(
                (
                    0,
                    0,
                    {
                        "sequence": sequence,
                        "model": model,
                        "table_name": table_name,
                        "missing_model": missing_model,
                        "orphan_count": orphan_count,
                    },
                )
            )
        if not res:
            raise UserError(_("No orphaned data entries found"))
        return res

    def _purge_batch(self):
        """Delete at most ``batch_size`` orphaned entries, without committing.

        :return: the number of data entries deleted
        """
        self.ensure_one()
        todo = self.batch_size
        purged = 0
        for line in self.line_ids.filtered(lambda ln: not ln.done):
            limit = min(todo, self.batch_size)
            ids = self._find_orphan_ids(line, limit)
            if ids:
                self.env["ir.model.data"].browse(ids).unlink()
                line.write(
                    {
                        "last_id": ids[-1],
                        "purged_count": line.purged_count + len(ids),
                    }
                )
                purged += len(ids)
                todo -= len(ids)
            if len(ids) < limit:
                # Everything matching this model has been processed.
                line.done = True
            if todo <= 0:
                break
        if purged:
            self.logger.info("Purged %s orphaned data entries in batch mode", purged)
        return purged

    def action_purge_batch(self):
        """Purge a single batch and commit it."""
        self.ensure_one()
        self._purge_batch()
        # Commit so that the next batch starts with a fresh transaction: this
        # keeps the transaction log small and the locks short.
        self.env.cr.commit()  # pylint: disable=invalid-commit
        return self._reload_action()

    def action_purge_all(self):
        """Purge all remaining orphaned entries, batch after batch."""
        self.ensure_one()
        while self.remaining_count:
            if not self._purge_batch():
                # Nothing purged although entries are left: avoid an endless
                # loop (the counts can be outdated if the database changed).
                _logger.warning(
                    "No orphaned data entry purged for wizard %s while %s "
                    "entries are supposed to remain",
                    self.id,
                    self.remaining_count,
                )
                break
            self.env.cr.commit()  # pylint: disable=invalid-commit
        return self._reload_action()

    def _reload_action(self):
        """Reopen the wizard so that the progress is refreshed."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Purge data entries in batches"),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "current",
        }

    @api.model
    def get_wizard_action(self):
        wizard = self.create({})
        return {
            "type": "ir.actions.act_window",
            "name": wizard._description,
            "views": [(False, "form")],
            "res_model": self._name,
            "res_id": wizard.id,
            "flags": {
                "action_buttons": False,
                "sidebar": False,
            },
        }
