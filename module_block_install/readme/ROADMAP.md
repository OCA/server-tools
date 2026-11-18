- A direct `write` on `ir.module.module.state` over RPC is not guarded: an
  administrator could mark a module `to install`, and it would be installed
  at the next deploy.
- "Import Module" (`base_import_module`) is not guarded.
- The `module_*` checkboxes in Settings could be made read-only when blocking
  is on, instead of refusing the whole save.
- Anyone with access to the server (`odoo shell`, `psql`, the command line)
  is not blocked, on purpose: that is how deployments work.
