# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""A transaction is one undoable step: everything a single user request did."""

import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .base import gu_suspend

_logger = logging.getLogger(__name__)

DEFAULT_RETENTION_DAYS = 30
DEFAULT_TRASH_RETENTION_DAYS = 180
VACUUM_BATCH = 1000


class GlobalUndoTransaction(models.Model):
    _name = "global.undo.transaction"
    _description = "Global Undo Transaction"
    _order = "id desc"

    user_id = fields.Many2one(
        "res.users", string="User", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one("res.company", string="Company", index=True)
    state = fields.Selection(
        [("done", "Applied"), ("undone", "Undone"), ("discarded", "Discarded")],
        default="done",
        required=True,
        index=True,
    )
    operation_ids = fields.One2many(
        "global.undo.operation", "transaction_id", string="Operations"
    )
    operation_count = fields.Integer(compute="_compute_summary")
    name = fields.Char(compute="_compute_summary")

    @api.depends(
        "operation_ids.kind", "operation_ids.res_name", "operation_ids.model_name"
    )
    def _compute_summary(self):
        labels = dict(
            self.env["global.undo.operation"]
            ._fields["kind"]
            ._description_selection(self.env)
        )
        # One lookup per distinct model instead of one per transaction: the
        # history list would otherwise query ir.model on every row.
        model_labels = {}
        for transaction in self:
            operations = transaction.operation_ids
            transaction.operation_count = len(operations)
            if not operations:
                transaction.name = _("Empty step")
                continue
            # Label the step after its newest operation: a nested create
            # journals the children first, so the newest one is the parent the
            # user actually thinks they created.
            main = operations.sorted("id")[-1]
            if main.model_name not in model_labels:
                model_labels[main.model_name] = (
                    self.env["ir.model"]._get(main.model_name).name or main.model_name
                )
            model_label = model_labels[main.model_name]
            if len(operations) == 1:
                transaction.name = _(
                    "%(action)s %(model)s: %(record)s",
                    action=labels.get(main.kind, main.kind),
                    model=model_label,
                    record=main.res_name or main.res_id,
                )
            else:
                transaction.name = _(
                    "%(action)s %(count)s %(model)s",
                    action=labels.get(main.kind, main.kind),
                    count=len(operations),
                    model=model_label,
                )

    # ------------------------------------------------------------------
    # Journalling
    # ------------------------------------------------------------------

    @api.model
    def _gu_current(self):
        """The step being recorded, one per user request.

        Grouping on the cursor is what makes a form save with its one2many
        children a single Ctrl+Z, since a request owns exactly one cursor.
        """
        cursor = self.env.cr
        current = self.browse(getattr(cursor, "gu_transaction_id", False)).exists()
        if current:
            return current
        current = self.sudo().create(
            {
                "user_id": self.env.uid,
                "company_id": self.env.company.id,
            }
        )
        cursor.gu_transaction_id = current.id
        # New history makes the redo stack unreachable, as in any editor.
        self.sudo().search(
            [("user_id", "=", self.env.uid), ("state", "=", "undone")]
        ).state = "discarded"
        return current

    @api.model
    def _gu_log(self, values_list):
        transaction = self._gu_current()
        for values in values_list:
            values["transaction_id"] = transaction.id
        operations = self.env["global.undo.operation"].sudo().create(values_list)
        transaction._gu_refresh_stamps(operations)

    def _gu_refresh_stamps(self, operations):
        """Realign earlier operations of this step on the same records.

        Saving a form creates a record and then writes to it; both are part of
        the same step, but the write moves ``write_date`` past what the creation
        recorded. Without this the step would look concurrently modified to
        itself and refuse to be undone.
        """
        self.ensure_one()
        stamps = {
            (operation.model_name, operation.res_id): operation.record_write_date
            for operation in operations
            if operation.record_write_date
        }
        if not stamps:
            return
        siblings = (
            self.env["global.undo.operation"]
            .sudo()
            .search(
                [
                    ("transaction_id", "=", self.id),
                    ("id", "not in", operations.ids),
                    ("model_name", "in", [model for model, _res_id in stamps]),
                ]
            )
        )
        for sibling in siblings:
            stamp = stamps.get((sibling.model_name, sibling.res_id))
            if (
                stamp
                and sibling.record_write_date
                and sibling.record_write_date < stamp
            ):
                sibling.record_write_date = stamp

    @api.model
    def _gu_log_create(self, records):
        snapshots = records._gu_snapshot()
        self._gu_log(
            [
                {
                    "kind": "create",
                    "model_name": records._name,
                    "res_id": record.id,
                    "res_name": record._gu_display_name(),
                    "record_write_date": record._gu_write_stamp(),
                    # Needed to re-create the record if the undo is later redone.
                    "values_after": json.dumps(snapshots[record.id], default=str),
                }
                for record in records
            ]
        )

    @api.model
    def _gu_log_write(self, records, before):
        # Every record of the batch was snapshotted on the same field names.
        fnames = list(next(iter(before.values()), ()))
        after = records._gu_snapshot(fnames)
        values_list = []
        for record in records:
            old, new = before.get(record.id, {}), after.get(record.id, {})
            changed = {name for name, value in old.items() if new.get(name) != value}
            if not changed:
                continue
            values_list.append(
                {
                    "kind": "write",
                    "model_name": records._name,
                    "res_id": record.id,
                    "res_name": record._gu_display_name(),
                    "record_write_date": record._gu_write_stamp(),
                    "values_before": json.dumps(
                        {name: old[name] for name in changed}, default=str
                    ),
                    "values_after": json.dumps(
                        {name: new[name] for name in changed}, default=str
                    ),
                }
            )
        if values_list:
            self._gu_log(values_list)

    @api.model
    def _gu_log_unlink(self, model_name, snapshots, names):
        self._gu_log(
            [
                {
                    "kind": "unlink",
                    "model_name": model_name,
                    "res_id": res_id,
                    "res_name": names.get(res_id),
                    "values_before": json.dumps(snapshot, default=str),
                }
                for res_id, snapshot in snapshots.items()
            ]
        )

    @api.model
    def _gu_log_action(self, model_name, method, undo_methods, targets):
        self._gu_log(
            [
                {
                    "kind": "action",
                    "model_name": model_name,
                    "res_id": res_id,
                    "res_name": res_name,
                    "record_write_date": stamp,
                    "method": method,
                    "undo_methods": json.dumps(list(undo_methods)),
                }
                for res_id, res_name, stamp in targets
            ]
        )

    # ------------------------------------------------------------------
    # Undo / redo
    # ------------------------------------------------------------------

    def _gu_ordered(self, direction):
        """Operations in the order they must be replayed.

        A nested create journals the children before their parent, so newest
        first is also parent first: on undo that lets the parent's delete
        cascade to the children, and on redo it makes the parent exist before
        the children that reference it. Everything else replays in the order it
        originally happened.
        """
        self.ensure_one()
        operations = self.operation_ids.sorted("id", reverse=True)
        if direction == "undo":
            return operations
        creations = operations.filtered(lambda operation: operation.kind == "create")
        return creations + (operations - creations).sorted("id")

    def _gu_apply(self, direction):
        """Replay this step backwards (``undo``) or forwards (``redo``)."""
        self.ensure_one()
        if self.user_id != self.env.user and not self.env.user.has_group(
            "global_undo.global_undo_group_manager"
        ):
            raise UserError(_("You can only undo your own operations."))
        operations = self._gu_ordered(direction)
        blockers = [
            reason
            for reason in (op._gu_blocker(direction) for op in operations)
            if reason
        ]
        if blockers:
            raise UserError(
                _(
                    "This operation cannot be %(direction)s:\n%(reasons)s",
                    direction=_("undone") if direction == "undo" else _("redone"),
                    reasons="\n".join(
                        "- " + reason for reason in dict.fromkeys(blockers)
                    ),
                )
            )
        # Old id -> new id of everything re-created along the way, so that
        # children restored after their parent point at the new parent.
        remap = {}
        # A half-applied step would be worse than none: the savepoint rolls the
        # whole thing back, cache included, if any operation fails.
        with self.env.cr.savepoint(), gu_suspend(self.env):
            for operation in operations:
                operation._gu_apply(direction, remap)
        # The replay itself just moved write_date on every record it touched.
        operations._gu_stamp()
        self.sudo().state = "undone" if direction == "undo" else "done"
        return self.name

    def action_undo(self):
        self._gu_apply("undo")
        return True

    def action_redo(self):
        self._gu_apply("redo")
        return True

    # ------------------------------------------------------------------
    # Client interface
    # ------------------------------------------------------------------

    @api.model
    def _gu_next(self, direction):
        """The step Ctrl+Z / Ctrl+Shift+Z would act on, if any.

        Undo takes the newest applied step; redo takes the oldest undone one,
        so that repeated redos walk back up the stack in the order it was
        unwound.
        """
        return self.search(
            [
                ("user_id", "=", self.env.uid),
                ("state", "=", "done" if direction == "undo" else "undone"),
            ],
            order="id desc" if direction == "undo" else "id asc",
            limit=1,
        )

    @api.model
    def gu_state(self):
        """Everything the systray needs, in one round trip."""
        undo, redo = self._gu_next("undo"), self._gu_next("redo")
        history = self.search([("user_id", "=", self.env.uid)], limit=10)
        return {
            "undo": {"id": undo.id, "name": undo.name} if undo else False,
            "redo": {"id": redo.id, "name": redo.name} if redo else False,
            "history": [
                {
                    "id": transaction.id,
                    "name": transaction.name,
                    "state": transaction.state,
                    "date": fields.Datetime.to_string(transaction.create_date),
                }
                for transaction in history
            ],
        }

    @api.model
    def gu_apply_next(self, direction):
        """Undo or redo the next step and report the outcome to the client."""
        transaction = self._gu_next(direction)
        if not transaction:
            return {
                "done": False,
                "message": (
                    _("Nothing left to undo.")
                    if direction == "undo"
                    else _("Nothing left to redo.")
                ),
                "state": self.gu_state(),
            }
        try:
            name = transaction._gu_apply(direction)
        except UserError as error:
            return {"done": False, "message": str(error), "state": self.gu_state()}
        return {
            "done": True,
            "message": (
                _("Undone: %(step)s", step=name)
                if direction == "undo"
                else _("Redone: %(step)s", step=name)
            ),
            "state": self.gu_state(),
        }

    # ------------------------------------------------------------------
    # Housekeeping
    # ------------------------------------------------------------------

    @api.model
    def _gu_vacuum(self):
        """Drop history past its retention window (cron).

        The trash keeps its own, longer window: forgetting that a record was
        deleted is a nuisance, but losing the only copy of it is data loss, so
        a step still holding recoverable records is kept until the trash window
        expires even though it can no longer be undone.
        """
        parameters = self.env["ir.config_parameter"].sudo()
        days = int(
            parameters.get_param("global_undo.retention_days", DEFAULT_RETENTION_DAYS)
        )
        trash_days = int(
            parameters.get_param(
                "global_undo.trash_retention_days", DEFAULT_TRASH_RETENTION_DAYS
            )
        )
        now = fields.Datetime.now()
        trash_limit = fields.Datetime.subtract(now, days=trash_days)
        expired = self.sudo().search(
            [
                ("create_date", "<", fields.Datetime.subtract(now, days=days)),
            ]
        )
        holding_trash = (
            self.env["global.undo.operation"]
            .sudo()
            .search(
                [
                    ("transaction_id", "in", expired.ids),
                    ("in_trash", "=", True),
                ]
            )
            .transaction_id
        )
        stale = (expired - holding_trash) | holding_trash.filtered(
            lambda transaction: transaction.create_date < trash_limit
        )
        _logger.info(
            "Global undo vacuum: removing %s transactions "
            "(history %s days, trash %s days)",
            len(stale),
            days,
            trash_days,
        )
        # Batched rather than one statement: a year of history can be hundreds
        # of thousands of rows. The cron commits once the job returns.
        for index in range(0, len(stale), VACUUM_BATCH):
            stale[index : index + VACUUM_BATCH].unlink()
