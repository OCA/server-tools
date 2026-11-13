# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Recording layer: every tracked create, write and unlink is journalled so it
can be replayed backwards (undo) or forwards (redo).

Odoo core is not modified: the hooks come from ``_inherit = "base"``.
"""

from collections import defaultdict
from contextlib import contextmanager

from odoo import api, fields, models
from odoo.http import request
from odoo.tools.misc import OrderedSet

# Never recorded. Technical plumbing, logs and messaging side effects: replaying
# them is either meaningless or actively harmful.
UNTRACKED_PREFIXES = (
    "global.undo.",
    "ir.",
    "bus.",
    "mail.",
    "base.",
    "report.",
    "iap.",
    "res.users.log",
    "res.users.settings",
)

# Never recorded either. These are ledger rows: the accounting and stock truth
# is stored here and is only allowed to change through the business layer that
# owns it. Writing them back directly would silently break integrity, so they
# are kept out of the journal entirely rather than recorded and then refused.
# Administrators can add their own through ``global.undo.exclusion``.
UNTRACKED_MODELS = frozenset(
    {
        "account.bank.statement.line",
        "account.full.reconcile",
        "account.move.line",
        "account.partial.reconcile",
        "account.payment",
        "account.tax.repartition.line",
        "pos.order",
        "pos.order.line",
        "product.price.history",
        "stock.move",
        "stock.move.line",
        "stock.quant",
        "stock.valuation.layer",
    }
)

# Fields that are never part of a snapshot: they are managed by the ORM itself.
UNTRACKED_FIELDS = frozenset(
    {"id", "create_uid", "create_date", "write_uid", "write_date"}
)

# Beyond this, the operation is a mass update and journalling it would cost more
# than it is worth. Such operations stay out of the history.
MAX_RECORDS = 200

# Attachments and images are stored so that restoring from the trash brings them
# back, but a single oversized file would bloat the journal for little gain.
MAX_BINARY_BYTES = 512 * 1024

# The ORM entry points the web client uses to change data on the user's behalf.
# Anything else it calls -- session bootstrap, onchange, name_search, or a
# housekeeping method such as res.company.iap_enrich_auto -- is the client
# talking to itself, and must not land on top of the user's undo stack.
USER_EDIT_METHODS = frozenset(
    {
        "action_archive",
        "action_unarchive",
        "copy",
        "create",
        "toggle_active",
        "unlink",
        "web_save",
        "write",
    }
)


@contextmanager
def gu_suspend(env):
    """Stop recording inside the block.

    Used while undoing or redoing, so the replay does not become new history,
    and while running a business action, since the action is the undoable unit
    rather than the dozens of writes it performs.

    The flag lives on the cursor because ``Environment`` and ``Transaction``
    both use ``__slots__``, and a cursor is exactly one database transaction.
    """
    cursor = env.cr
    cursor.gu_suspended = getattr(cursor, "gu_suspended", 0) + 1
    try:
        yield
    finally:
        cursor.gu_suspended -= 1


class GuThrowAwayCache:
    """Read field values without poisoning the caller's ORM cache.

    Snapshots intentionally run as superuser so restricted and multi-company
    fields are stored whole. Without an isolated cache those values stick on
    the current env and later raise AccessError (or return the wrong company)
    when the real user reads the same record — the exact failure
    ``test_auditlog`` multi-company product tax cases catch when this module
    is installed alongside auditlog.
    """

    def __init__(self, env):
        self._transaction = env.transaction

    def __enter__(self):
        self._original_cache = self._transaction.cache
        self._original_tocompute = self._transaction.tocompute
        temporary_cache = api.Cache()
        temporary_tocompute = defaultdict(OrderedSet)
        for env in self._transaction.envs:
            env.cache = temporary_cache
        self._transaction.cache = temporary_cache
        self._transaction.tocompute = temporary_tocompute
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for env in self._transaction.envs:
            env.cache = self._original_cache
        self._transaction.cache = self._original_cache
        self._transaction.tocompute = self._original_tocompute


def gu_is_user_edit():
    """Whether the current request is the user changing data through the UI.

    Without a request there is no client to second-guess (shell, cron, tests),
    so the operation counts. With one, only the web client's save, delete and
    archive calls and its button presses do.
    """
    if not request:
        return True
    path = request.httprequest.path
    if path.startswith("/web/dataset/call_button"):
        return True
    return (
        path.startswith("/web/dataset/call_kw")
        and request.params.get("method") in USER_EDIT_METHODS
    )


def gu_dump(field, value):
    """Turn a field value into something JSON can store."""
    if field.type == "many2one":
        return value.id or False
    if field.type in ("many2many", "one2many"):
        return value.ids
    if field.type == "reference":
        return f"{value._name},{value.id}" if value else False
    if field.type == "datetime":
        return fields.Datetime.to_string(value) if value else False
    if field.type == "date":
        return fields.Date.to_string(value) if value else False
    if field.type == "html":
        return str(value) if value else False
    if field.type == "binary":
        if not value or len(value) > MAX_BINARY_BYTES:
            return False
        # Stored binaries already come back base64 encoded, as bytes.
        return value.decode() if isinstance(value, bytes) else value
    return value


class Base(models.AbstractModel):
    _inherit = "base"

    # CRUD methods

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if records._gu_is_tracked():
            # After-snapshots use an isolated cache that reloads from the DB
            # (see GuThrowAwayCache). Flush so the journal sees what we just
            # wrote, not the pre-write row.
            records.flush_recordset()
            self.env["global.undo.transaction"]._gu_log_create(records)
        return records

    def write(self, vals):
        tracked = self._gu_is_tracked()
        before = self._gu_snapshot(list(vals)) if tracked else None
        result = super().write(vals)
        if tracked:
            # Without a flush the after-snapshot would equal the before one
            # (stale DB row) and the write would never be journalled — undo
            # would then hit the previous step instead (e.g. delete a create).
            self.flush_recordset()
            self.env["global.undo.transaction"]._gu_log_write(self, before)
        return result

    def unlink(self):
        tracked = self._gu_is_tracked()
        snapshots = names = None
        if tracked:
            # Everything must be read before the rows are gone.
            self.flush_recordset()
            snapshots = self._gu_snapshot()
            names = {record.id: record._gu_display_name() for record in self}
        result = super().unlink()
        if tracked:
            self.env["global.undo.transaction"]._gu_log_unlink(
                self._name, snapshots, names
            )
        return result

    # Business methods

    def _gu_is_tracked(self):
        """Whether operations on ``self`` belong in the undo journal."""
        if self._transient or self._abstract or self._name in UNTRACKED_MODELS:
            return False
        if self._name.startswith(UNTRACKED_PREFIXES):
            return False
        if len(self) > MAX_RECORDS:
            return False
        env = self.env
        if env.su or not env.uid or not env.registry.ready:
            return False
        if getattr(env.cr, "gu_suspended", 0):
            return False
        if not gu_is_user_edit():
            return False
        if self._name in env["global.undo.exclusion"]._gu_excluded_models():
            return False
        return env.user.has_group("global_undo.global_undo_group_user")

    def _gu_recordable_fields(self):
        """Stored fields whose value can be written back verbatim.

        Odoo 18 declares most user-editable fields as computed but writable
        (``compute=..., store=True, readonly=False``) -- quantities, unit
        prices, dates -- so only genuinely read-only computed fields are left
        out. Related fields belong to another record and one2many children have
        their own lifecycle. Binaries are kept, but only the source field: the
        resized variants of an image are recomputed from it anyway.
        """
        for name, field in self._fields.items():
            if name in UNTRACKED_FIELDS or not field.store:
                continue
            if field.type in ("one2many", "properties", "properties_definition"):
                continue
            if field.type == "binary" and field.compute:
                continue
            if field.related or (
                field.compute and field.readonly and not field.inverse
            ):
                continue
            yield name, field

    def _gu_snapshot(self, fnames=None):
        """Return ``{record_id: {field_name: json_value}}`` for ``self``.

        Read with elevated rights on purpose. A model may carry stored fields
        restricted to another group -- ``res.partner.signup_type`` is one --
        and reading them as the acting user would make deleting an ordinary
        contact fail outright. The snapshot is a faithful copy of the row so
        that an undo puts it back whole; the views only show it to managers.
        """
        recordable = dict(self._gu_recordable_fields())
        if fnames is not None:
            recordable = {
                name: recordable[name] for name in fnames if name in recordable
            }
        # Plain JSON values only: disposable cache so the sudo read does not
        # leak inaccessible multi-company / group-restricted records into the
        # caller's env (see GuThrowAwayCache).
        with GuThrowAwayCache(self.env):
            return {
                record.id: {
                    name: gu_dump(field, record[name])
                    for name, field in recordable.items()
                }
                for record in self.sudo()
            }

    def _gu_write_vals(self, data):
        """Turn a snapshot back into values accepted by ``create`` or ``write``."""
        vals = {}
        for name, value in data.items():
            field = self._fields.get(name)
            if field is None:
                continue
            if field.type == "many2many":
                vals[name] = [fields.Command.set(value or [])]
            elif field.type == "binary":
                vals[name] = value.encode() if value else False
            else:
                vals[name] = value
        return vals

    def _gu_display_name(self):
        """``display_name`` that never raises: it is only used as a log label."""
        self.ensure_one()
        try:
            return self.display_name
        except Exception:  # pylint: disable=broad-except
            return f"{self._name},{self.id}"

    def _gu_write_stamp(self):
        """``write_date`` observed right after an operation, for conflict checks."""
        self.ensure_one()
        return self.write_date if self._log_access else False
