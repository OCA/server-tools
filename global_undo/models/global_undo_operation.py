# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""One journalled operation, and the rules deciding whether it may be replayed."""

import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .base import gu_suspend

# Access right required to replay an operation in each direction.
REQUIRED_ACCESS = {
    ("create", "undo"): "unlink",
    ("create", "redo"): "create",
    ("write", "undo"): "write",
    ("write", "redo"): "write",
    ("unlink", "undo"): "create",
    ("unlink", "redo"): "unlink",
    ("action", "undo"): "write",
    ("action", "redo"): "write",
}


class GlobalUndoOperation(models.Model):
    _name = "global.undo.operation"
    _description = "Global Undo Operation"
    _order = "id desc"

    transaction_id = fields.Many2one(
        "global.undo.transaction",
        required=True,
        index=True,
        ondelete="cascade",
    )
    kind = fields.Selection(
        [
            ("create", "Created"),
            ("write", "Updated"),
            ("unlink", "Deleted"),
            ("action", "Executed"),
        ],
        required=True,
        index=True,
    )
    model_name = fields.Char(string="Model", required=True, index=True)
    res_id = fields.Integer(string="Record ID", required=True)
    res_name = fields.Char(string="Record")
    # A record restored from the trash gets a fresh database id; later replays
    # must follow it instead of the original one.
    restored_res_id = fields.Integer()
    # The record's write_date as it stood right after this operation, and after
    # every replay of it. Anything else means somebody edited the record in the
    # meantime and undoing would silently discard their work. An exact match is
    # used rather than a time window: the journal writes the value it read, so
    # two edits within the same second are still two different values.
    record_write_date = fields.Datetime()
    values_before = fields.Text()
    values_after = fields.Text()
    method = fields.Char(help="Business method that was executed.")
    undo_methods = fields.Char(
        help="JSON list of methods that revert the executed one."
    )

    user_id = fields.Many2one(related="transaction_id.user_id", store=True, index=True)
    company_id = fields.Many2one(
        related="transaction_id.company_id", store=True, index=True
    )
    state = fields.Selection(related="transaction_id.state", store=True)
    # Deleted records still in the trash: never restored, and the deletion itself
    # has not been undone.
    in_trash = fields.Boolean(compute="_compute_in_trash", store=True)

    @api.depends("kind", "restored_res_id", "state")
    def _compute_in_trash(self):
        for operation in self:
            operation.in_trash = (
                operation.kind == "unlink"
                and not operation.restored_res_id
                and operation.state != "undone"
            )

    # ------------------------------------------------------------------
    # Replay
    # ------------------------------------------------------------------

    def _gu_target(self):
        self.ensure_one()
        return self.env[self.model_name].browse(self.restored_res_id or self.res_id)

    def _gu_stamp(self):
        """Record the target's current ``write_date`` as this operation's baseline."""
        for operation in self:
            if operation.model_name not in self.env:
                continue
            record = operation._gu_target().exists()
            operation.sudo().record_write_date = (
                record._gu_write_stamp() if record else False
            )

    def _gu_blocker(self, direction):
        """Human readable reason why this cannot be replayed, or ``None``."""
        self.ensure_one()
        if self.model_name not in self.env:
            return _("Model %(model)s is no longer installed.", model=self.model_name)
        model = self.env[self.model_name]
        access = REQUIRED_ACCESS[(self.kind, direction)]
        if not model.browse().has_access(access):
            return _(
                "You are not allowed to %(access)s %(model)s records.",
                access=access,
                model=self.model_name,
            )

        recreating = (self.kind, direction) in (("unlink", "undo"), ("create", "redo"))
        record = self._gu_target().exists()
        if recreating:
            if record:
                return _(
                    "%(record)s already exists.",
                    record=self.res_name or self.model_name,
                )
            return None
        if not record:
            return _(
                "%(record)s no longer exists.", record=self.res_name or self.model_name
            )
        if not record.has_access(access):
            return _(
                "You are not allowed to %(access)s %(record)s.",
                access=access,
                record=self.res_name or self.model_name,
            )
        if (
            "company_id" in model._fields
            and record.company_id
            and record.company_id.id not in self.env.companies.ids
        ):
            return _(
                "%(record)s belongs to a company you are not working in.",
                record=self.res_name,
            )
        # Applies to undoing a creation too: deleting the record would take
        # somebody else's later edits down with it.
        if (
            self.record_write_date
            and record._gu_write_stamp() != self.record_write_date
        ):
            return _(
                "%(record)s changed after this operation; undoing it would "
                "discard newer edits.",
                record=self.res_name or self.model_name,
            )
        return self._gu_integrity_blocker(record, direction)

    def _gu_integrity_blocker(self, record, direction):
        """Accounting and stock rules that outrank the undo history."""
        if self.model_name == "account.move":
            if record.inalterable_hash:
                return _(
                    "%(record)s is secured by a hash and can no longer be changed.",
                    record=self.res_name,
                )
            if record.state == "posted" and self.kind != "action":
                return _(
                    "%(record)s is posted; only its posting can be undone.",
                    record=self.res_name,
                )
            if (
                self.kind == "action"
                and direction == "undo"
                and record.payment_state not in ("not_paid", False)
            ):
                return _(
                    "%(record)s is reconciled or paid; unpost it manually first.",
                    record=self.res_name,
                )
        if self.model_name == "stock.picking" and record.state == "done":
            return _(
                "%(record)s is already done; stock moves cannot be reverted "
                "automatically.",
                record=self.res_name,
            )
        return None

    def _gu_apply(self, direction, remap=None):
        """Replay this operation.

        Operations whose target has vanished mid-step are skipped rather than
        failing: deleting a parent cascades to children that carry their own
        journal entries, and reaching the intended state early is a success.

        The replay runs with elevated rights. ``_gu_blocker`` is the gate that
        decides whether this user may touch this record; past it, the snapshot
        has to go back verbatim, including stored fields whose own group the
        user is not in and which they were never able to set by hand.
        """
        self.ensure_one()
        if (self.kind, direction) in (("unlink", "undo"), ("create", "redo")):
            self._gu_restore(remap)
            return
        record = self._gu_target().sudo().exists()
        if not record:
            return
        if self.kind == "action":
            methods = (
                json.loads(self.undo_methods) if direction == "undo" else [self.method]
            )
            for name in methods:
                getattr(record, name)()
        elif (self.kind, direction) in (("create", "undo"), ("unlink", "redo")):
            record.unlink()
            # The restored copy is gone: a later restore must start over, and the
            # deletion belongs back in the trash.
            self.sudo().restored_res_id = False
        else:
            data = json.loads(
                (self.values_before if direction == "undo" else self.values_after)
                or "{}"
            )
            record.write(self.env[self.model_name]._gu_write_vals(data))

    def _gu_restore(self, remap=None):
        """Re-create the record from its snapshot, under a new database id.

        ``remap`` carries ``{(model, old_id): new_id}`` for records already
        restored in this step, so children re-created after their parent point
        at the parent's new id instead of the dead one.
        """
        model = self.env[self.model_name].sudo()
        data = json.loads(self.values_before or self.values_after or "{}")
        vals = model._gu_write_vals(data)
        for name, value in vals.items():
            field = model._fields[name]
            if field.type == "many2one" and value and remap:
                vals[name] = remap.get((field.comodel_name, value), value)
        record = model.create(vals)
        self.sudo().restored_res_id = record.id
        if remap is not None:
            remap[(self.model_name, self.res_id)] = record.id

    # ------------------------------------------------------------------
    # Trash
    # ------------------------------------------------------------------

    def _gu_restore_order(self):
        """Parents before children, as in a transaction replay.

        A nested delete journals the children before their parent, so replaying
        newest first re-creates the parent before the records that point at it.
        """
        return self.sorted("id", reverse=True)

    def action_restore(self):
        """Restore deleted records straight from the trash view.

        Restoring a parent and its children together goes through the same
        ordering and id remapping as an undo, otherwise the children would come
        back pointing at the parent's dead id.
        """
        operations = self._gu_restore_order()
        remap = {}
        # All or nothing: a half-restored parent is worse than none at all.
        with self.env.cr.savepoint(), gu_suspend(self.env):
            for operation in operations:
                if not operation.in_trash:
                    raise UserError(
                        _("%(record)s is not in the trash.", record=operation.res_name)
                    )
                blocker = operation._gu_blocker("undo")
                if blocker:
                    raise UserError(blocker)
                operation._gu_restore(remap)
        operations._gu_stamp()
        return True

    def action_open_record(self):
        self.ensure_one()
        record = self._gu_target()
        if not record.exists():
            raise UserError(
                _(
                    "%(record)s no longer exists.",
                    record=self.res_name or self.model_name,
                )
            )
        return {
            "type": "ir.actions.act_window",
            "res_model": self.model_name,
            "res_id": record.id,
            "view_mode": "form",
            "target": "current",
        }
