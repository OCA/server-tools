In standard Odoo, clicking **Upgrade** on a module also queues all installed
modules that depend on it. On large databases and during frequent development
this slows things down: often you only need to upgrade a single module, without
cascading upgrades of its dependents.

A way is needed to start an upgrade for the selected module only (and install
any missing dependencies if they are not yet installed), without adding
reverse-dependencies to the upgrade.
