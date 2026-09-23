The auditlog module stores audit data in PostgreSQL. In production systems with extensive audit rules, these tables grow without limits, causing three issues:

- Database bloat;
- Immutability gap: Members of group_auditlog_manager (implied by base.group_system) have full CRUD access to audit tables, allowing audit records to be altered or deleted via UI, ORM, or SQL;
- Performance overhead: Audit logging runs synchronously in the same transaction and performs multiple ORM create() calls, adding latency to audited operations.
