## Groups

* **Global Undo: User**, implied by *Internal User*. Only the operations of
  users in this group are journalled. Removing the group disables recording for
  that user entirely.
* **Global Undo: Administrator**, implied by *Settings*. Can review and undo
  the operations of every user, and read the stored snapshots.

## Undoable actions

*Settings > Global Undo > Configuration > Undoable Actions* declares which
business methods may be undone and which methods revert them, in order.

Three are shipped and activate themselves when their module is installed:

| Model | Action | Reverted with |
| --- | --- | --- |
| `sale.order` | `action_confirm` | `_action_cancel`, `action_draft` |
| `purchase.order` | `button_confirm` | `button_cancel`, `button_draft` |
| `account.move` | `action_post` | `button_draft` |

Add a line to cover a method of your own, or to change the inverse of one of
the three. Archiving a line that matches a shipped default switches that
default off. Changes take effect when the registry reloads.

## Excluded models

*Settings > Global Undo > Configuration > Excluded Models* takes any model out
of the journal, on top of the technical and ledger models the module always
leaves alone.

## Retention

A daily cron purges the history. Two separate windows, because forgetting that
something was deleted is a nuisance while losing the only copy of it is data
loss:

* `global_undo.retention_days` (30 by default) for the history;
* `global_undo.trash_retention_days` (180 by default) for the steps still
  holding recoverable records. Such a step survives the first window even
  though it can no longer be undone.
