To configure this module, you need to:

1. Make sure the PostgreSQL extension `pg_clickhouse` is installed and available
   on the PostgreSQL server used by Odoo.

2. Make sure the ClickHouse database is reachable from the Odoo server.

3. Make sure the audit log tables already exist in ClickHouse.

4. Activate developer mode in Odoo.

5. Go to *Settings > Technical > Auditlog > ClickHouse Configurations*.

6. Open the active ClickHouse configuration used for audit log export.

7. Fill in or verify the connection parameters:

   - *Hostname or IP*
   - *TCP Port*
   - *Database name*
   - *User*
   - *Password*

8. Use *Test Connection* to verify that Odoo can connect to ClickHouse.

9. Use *Create Auditlog Tables* if the ClickHouse audit log tables have not yet
   been created.

10. Click *Enable FDW read* to switch standard Odoo audit log views to
    ClickHouse-backed foreign tables.

Important notes:

- Only the active ClickHouse configuration can enable FDW read.
- The PostgreSQL user used by Odoo must have the required privileges to create
  and use FDW objects.
- While FDW read is enabled, the active ClickHouse configuration cannot be
  deactivated, deleted, or changed for connection-related fields until FDW read
  is disabled.
