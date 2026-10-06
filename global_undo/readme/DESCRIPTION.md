This module journals what a user does in the backend and lets them take it
back with **Ctrl+Z** (**Cmd+Z** on macOS), or replay it with
**Ctrl+Shift+Z**:

* creations, updates and deletions, grouped one step per saved form, so that a
  form and its one2many lines are a single undo;
* business actions that have a known inverse, such as confirming a sales order
  or posting a journal entry;
* a history view and a trash from which deleted records can be restored.

Permissions, record rules, multi-company and accounting integrity are all
checked before anything is replayed. When a step cannot be replayed safely the
module refuses with a clear message rather than leaving the database
inconsistent.

Odoo core is not modified. The CRUD hooks come from an `_inherit = "base"`
model and the business action hooks from `_register_hook`, the same technique
`base_automation` uses.
