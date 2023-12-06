In odoo, by default some modules are marked as auto installable by the
`auto_install` key present in the manifest.

- This feature is very useful for "glue" modules that allow two modules
  to work together. (A typical example is `sale_stock` which allows
  `sale` and `stock` modules to work together).
- However, Odoo SA also marks some modules as auto installable, even
  though this is not technically required. This can happen for modules
  the company wants to promote like `iap`, modules with a big wow effect
  like `partner_autocomplete`, or some modules they consider useful by
  default like `account_edi`. See the discussion:
  <https://github.com/odoo/odoo/issues/71190>

This module allows to change by configuration, the list of auto
installable modules, adding or removing some modules to auto install.
