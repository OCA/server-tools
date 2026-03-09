To use this module, you need to:

1. Go to *Settings > Technical > Auditlog > ClickHouse Configurations*.

2. Open the active ClickHouse configuration.

3. Click *Enable FDW read*.

4. Open the standard audit log menus in Odoo:

   - *Settings > Technical > Audit > Logs*

5. Review audit log records as usual from the standard Odoo interface.

6. Use the existing search, filters, and group by options in audit log views to
   analyze audit data stored in ClickHouse.

7. Open an audited record and use the standard *View Logs* action when
   available. The action continues to open the related audit log entries through
   the standard Odoo interface.

Important notes:

- While FDW read mode is enabled, audit log records are read-only in Odoo.
- To return to local PostgreSQL audit log tables, go back to the active
  ClickHouse configuration and click *Disable FDW read*.
