Some operations cannot be undone. The module prefers to refuse with a clear
message over leaving the database inconsistent.

## Never recorded

These do not appear in the history at all.

* **Technical models.** Everything under `ir.`, `bus.`, `mail.`,
  `base.`, `report.`, `iap.`, plus `res.users.log` and
  `res.users.settings`. This covers module installation, views, crons,
  sequences, chatter messages, activities and notifications.
* **Ledger rows**, where the accounting and stock truth lives and which may
  only change through the business layer that owns it: `account.move.line`,
  `account.payment`, `account.partial.reconcile`, `account.full.reconcile`,
  `account.bank.statement.line`, `account.tax.repartition.line`,
  `stock.move`, `stock.move.line`, `stock.quant`,
  `stock.valuation.layer`, `pos.order` and its lines, and
  `product.price.history`.
* **Transient and abstract models**, which have no rows to put back.
* **Operations touching more than 200 records at once.** A mass update is
  cheaper to redo by hand than to journal.
* **Anything done as superuser or with `sudo()`**, during a module install or
  upgrade, or while the registry is not ready.
* **Anything that is not the user editing data through the web client.** Only
  the client's save, delete and archive calls and its button presses count.
  Imports, XML-RPC, the portal, the website and the client's own housekeeping
  calls are not journalled, so they never land on top of somebody's undo stack.

## Recorded, but the undo is refused

* **The record changed afterwards.** Every operation stores the `write_date`
  it read right after running, and stores it again on every replay. If it no
  longer matches exactly, somebody else touched the record and undoing would
  discard their work. This also applies to undoing a creation: deleting the
  record would take the other user's edits with it.
* **The permission is no longer there.** Undoing a creation requires delete
  rights, undoing a deletion requires create rights. Both model-level access
  and record-level rules are checked.
* **The record belongs to a company outside your allowed companies.**
* **The record is gone**, or, for something being re-created, already exists.
* **Journal entries.** An `account.move` carrying an `inalterable_hash`
  cannot be touched at all. A posted entry refuses plain field changes, since
  the only reversible thing about it is the posting itself. A reconciled or
  paid entry refuses to be set back to draft. Beyond that, Odoo's own
  `button_draft` rules (lock dates, sequence, hashed journals) apply and
  their error is propagated as is.
* **Transfers already done.** A `stock.picking` in state `done` is not
  reverted: the correct reversal is a return, not a deletion.
* **Another user's operations**, unless you are a Global Undo Administrator.

## Undone, with a caveat worth knowing

* **A restored record gets a new database id.** The ORM will not reuse a
  deleted one. The new id is kept in `restored_res_id` and later replays
  follow it, but any external reference to the old id stays broken -- and in
  most cases already was, since the deletion cascaded or nulled it.
* **One2many children do not come back on their own.** They have their own
  lifecycle and were deleted as separate operations. Restore them together with
  their parent from the trash and the link is rebuilt.
* **Binary fields are stored only up to 512 KB.** Larger attachments and images
  are dropped rather than bloat the journal. The computed variants of an image
  are not stored either, since they are regenerated from the original.
* **Read-only computed fields and related fields are not stored**, because they
  are recomputed from the fields that are.
* **Sequences are consumed.** Undoing the creation of an invoice does not give
  its number back to `ir.sequence`. A redo restores the original number from
  the snapshot.
* **External effects are not reverted.** Sent emails, webhooks, third party API
  calls and files written to disk are outside the database.
* **The chatter is not cleaned up.** Messages and followers created by the
  original operation stay, because `mail.*` is not recorded.
