Business need:

In some deployments, audit logs grow quickly and become expensive to keep and
query only in PostgreSQL. At the same time, auditors and administrators still
need to review audit trails from the standard Odoo interface without learning
new tools or getting direct access to external databases.

This module is useful in environments where audit log storage is moved to
ClickHouse, but end users must continue working with the standard Odoo Audit Log
screens.

Approach:

The module keeps the usual Odoo audit log interface while changing the read
source behind it. Instead of reading audit log data from local PostgreSQL audit
tables, Odoo can read it through PostgreSQL foreign tables backed by ClickHouse.

This allows administrators to keep the familiar menus, forms, filters, and
grouping options while using ClickHouse as the effective source for audit log
reads.

Useful information:

The module is especially useful in databases with high audit log volumes or in
setups where audit data should be stored outside the main PostgreSQL audit
tables.

When FDW read mode is enabled, audit log records are read-only in Odoo. If
needed, administrators can disable FDW read mode and restore reading from the
local PostgreSQL audit log tables.
