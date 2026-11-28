Create and update records in one or more remote Odoo instances via XML-RPC.

Key features:

- **Remote instances**: configure connections to remote Odoo servers (URL,
  database, username and password) with a built-in test-connection button.
- **Match configuration**: define per-model how to locate the equivalent
  record on the remote side:
  - By External ID (xmlid), falling back to match fields when no xmlid exists.
  - By match fields with two strategies: compound key (all fields combined)
    or alternative keys (first field that resolves a single result wins).
  - Recursive match for many2one fields without an xmlid, resolved using
    the match configuration of the related model.
- **Separate field sets**: distinct fields for create and update operations;
  if left empty, all stored scalar and many2one fields are used automatically.
- **Configurable operation**: create and update, create only, or update only.
- **Automatic server action**: saving a match configuration automatically
  creates a server action bound to the model, which appears in list and form
  views and opens the export wizard.
- **Export wizard**: choose target instances, operation and match fields for
  the current run; displays a result summary with counters per instance.
