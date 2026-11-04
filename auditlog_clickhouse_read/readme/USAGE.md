To use this module, you need to:

1. Click *Enable FDW read*.

2. Open the standard audit log menus in Odoo:

   - *Settings > Technical > Audit > Logs*

3. Review audit log records as usual from the standard Odoo interface.

4. Use the existing search, filters, and group-by options in audit log views to
   analyze audit data stored in ClickHouse.

5. Open an audited record and use the standard *View Logs* action when
   available. The action continues to open the related audit log entries through
   the standard Odoo interface.

Important notes:

- While FDW read mode is enabled, audit log records are read-only in Odoo.
- To return to local PostgreSQL audit log tables, go back to the active
  ClickHouse configuration and click *Disable FDW read*.
