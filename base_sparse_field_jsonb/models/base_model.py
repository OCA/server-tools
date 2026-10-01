"""Override Base model to handle GIN indexes before column conversion.

This module ensures GIN indexes on TEXT columns are dropped before
Odoo's _auto_init tries to convert columns, preventing the error:
"data type text has no default operator class for access method gin"
"""

import logging

from psycopg2 import Error as Psycopg2Error
from psycopg2 import sql

from odoo import models

_logger = logging.getLogger(__name__)


class BaseModelGinIndexHandler(models.AbstractModel):
    """Mixin to handle GIN indexes on TEXT columns during _auto_init.

    This is applied to models.Base to ensure GIN indexes are dropped
    before any column type conversion is attempted.
    """

    _inherit = "base"

    def _auto_init(self):
        """Override to drop GIN indexes on TEXT columns before column updates.

        PostgreSQL cannot convert a TEXT column to JSONB (or handle it properly)
        if there's a GIN index on it. We need to drop these indexes BEFORE
        any column processing happens.
        """
        # Get table name for this model
        table_name = self._table

        try:
            # Use the same cursor as the main transaction
            cr = self.env.cr

            # Check if table exists
            cr.execute(
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_name = %s AND table_schema = 'public'
                """,
                (table_name,),
            )
            if cr.fetchone():
                # Find and drop any GIN indexes for this table
                dropped = _drop_gin_indexes_on_text_columns_for_table(cr, table_name)
                if dropped:
                    _logger.warning(
                        "Dropped %d GIN indexes on %s before _auto_init",
                        dropped,
                        table_name,
                    )
        except Exception as e:
            # If we can't drop indexes, log and continue
            _logger.warning(
                "Could not check/drop GIN indexes for %s: %s",
                table_name,
                e,
            )

        return super()._auto_init()


def _drop_gin_indexes_on_text_columns_for_table(cr, table_name):
    """Drop all GIN indexes on tables with serialized fields.

    This drops ALL GIN indexes on the table to ensure column conversions
    can proceed. The indexes will be recreated on JSONB columns by the
    post_init_hook.

    Args:
        cr: Database cursor
        table_name: Name of the table to check

    Returns:
        int: Number of indexes dropped
    """
    # Check if this table has any column matching serialized field patterns
    # Don't check data_type - column might be TEXT or already JSONB
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = %s
          AND table_schema = 'public'
          AND (column_name LIKE 'x_custom_json%%' OR column_name LIKE '%%_json_attrs')
        LIMIT 1
        """,
        (table_name,),
    )
    if not cr.fetchone():
        # No serialized columns, nothing to do
        return 0

    _logger.debug(
        "Table %s has serialized columns, checking for GIN indexes", table_name
    )

    # Find ALL GIN indexes on this table (in public schema)
    cr.execute(
        """
        SELECT i.relname AS index_name
        FROM pg_index ix
        JOIN pg_class t ON t.oid = ix.indrelid
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_am am ON am.oid = i.relam
        JOIN pg_namespace n ON n.oid = t.relnamespace
        WHERE t.relname = %s
          AND n.nspname = 'public'
          AND am.amname = 'gin'
        """,
        (table_name,),
    )
    indexes = cr.fetchall()

    if not indexes:
        _logger.debug("No GIN indexes found on table %s", table_name)
        return 0

    _logger.info(
        "Found %d GIN indexes on table %s: %s", len(indexes), table_name, indexes
    )

    dropped = 0
    for (index_name,) in indexes:
        _logger.info(
            "Dropping GIN index '%s' on table %s before _auto_init",
            index_name,
            table_name,
        )
        try:
            drop_query = sql.SQL("DROP INDEX IF EXISTS {index}").format(
                index=sql.Identifier(index_name),
            )
            cr.execute(drop_query)
            dropped += 1
            _logger.info("Successfully dropped GIN index %s", index_name)
        except Psycopg2Error as e:
            _logger.error("Could not drop GIN index %s: %s", index_name, e)

    return dropped
