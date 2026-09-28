This module extends the audit log integration with ClickHouse to let Odoo read
audit log data through PostgreSQL Foreign Data Wrapper (FDW).

When FDW read mode is enabled, standard Odoo audit log views continue to work
without additional user tools or direct database access, while the data is read
from ClickHouse. Audit log records become read-only in Odoo while this mode is
active.
