Once auditlog_clickhouse_write is installed and configured:

- Users perform tracked operations (create, write, unlink, read, export) on models with active auditlog.rule subscriptions.
  This behavior is unchanged from the base auditlog module.
- Log data is serialized and stored in the local auditlog.log.buffer table instantly. The standard auditlog tables are not populated.
- Every 5 minutes (default), the Cron job runs, pushes data to ClickHouse, and cleans the local buffer.
- Data is permanently stored in ClickHouse and cannot be modified or deleted via Odoo.
