"""Installation hooks for base_sparse_field_jsonb.

The pre_init_hook handles:
1. Dropping existing GIN indexes on TEXT columns (they can't be converted)

The post_init_hook handles:
1. Migration of existing TEXT columns to JSONB
2. Creation of GIN indexes on JSONB columns for fast filtering
"""

import logging

from psycopg2 import Error as Psycopg2Error
from psycopg2 import sql

_logger = logging.getLogger(__name__)

# Tables that commonly have serialized fields (x_custom_json_attrs)
# This list covers the main models used with attribute_set
KNOWN_SERIALIZED_TABLES = [
    "product_template",
    "product_product",
    "res_partner",
    # Add more tables as needed
]


def drop_gin_indexes_on_text_columns(cr):
    """Drop all GIN indexes on TEXT columns that look like serialized fields.

    This function can be called from pre_init_hook or directly from
    other modules to ensure GIN indexes on TEXT columns are dropped
    before any TEXT-to-JSONB conversion is attempted.

    Args:
        cr: Database cursor
    """
    _logger.info("Checking for GIN indexes on TEXT columns...")

    # Find ALL GIN indexes on TEXT columns (not just serialized field patterns)
    # This is more comprehensive to catch all potential issues
    cr.execute(
        """
        SELECT
            t.relname AS table_name,
            a.attname AS column_name,
            i.relname AS index_name,
            pg_get_indexdef(ix.indexrelid) AS index_def
        FROM pg_index ix
        JOIN pg_class t ON t.oid = ix.indrelid
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_attribute a ON a.attrelid = t.oid
        JOIN pg_am am ON am.oid = i.relam
        JOIN information_schema.columns c
            ON c.table_name = t.relname
            AND c.column_name = a.attname
        WHERE am.amname = 'gin'
          AND c.data_type = 'text'
          AND a.attnum = ANY(ix.indkey)
          AND t.relkind = 'r'
        ORDER BY t.relname, a.attname
        """
    )
    indexes_to_drop = cr.fetchall()

    if not indexes_to_drop:
        _logger.info("No GIN indexes on TEXT columns found.")
        return 0

    dropped_count = 0
    for table_name, column_name, index_name, _index_def in indexes_to_drop:
        _logger.warning(
            "Found GIN index '%s' on TEXT column %s.%s - dropping before conversion",
            index_name,
            table_name,
            column_name,
        )
        try:
            drop_query = sql.SQL("DROP INDEX IF EXISTS {index}").format(
                index=sql.Identifier(index_name),
            )
            cr.execute(drop_query)
            dropped_count += 1
            _logger.info("Successfully dropped GIN index %s", index_name)
        except Psycopg2Error as e:
            _logger.error(
                "Could not drop GIN index %s: %s",
                index_name,
                e,
            )

    _logger.info(
        "Dropped %d GIN indexes from TEXT columns.",
        dropped_count,
    )
    return dropped_count


def pre_init_hook(env):
    """Pre-installation hook to drop GIN indexes on TEXT columns.

    GIN indexes on TEXT columns will fail when Odoo tries to convert
    the column to JSONB. We need to drop them first, then recreate
    them on JSONB columns in post_init_hook.
    """
    cr = env.cr

    _logger.info("base_sparse_field_jsonb: Running pre_init_hook...")

    # Use the comprehensive function to drop ALL GIN indexes on TEXT columns
    dropped_count = drop_gin_indexes_on_text_columns(cr)

    if dropped_count > 0:
        _logger.info(
            "base_sparse_field_jsonb: Dropped %d GIN indexes from TEXT columns. "
            "They will be recreated on JSONB columns in post_init_hook.",
            dropped_count,
        )
    else:
        _logger.info("base_sparse_field_jsonb: No GIN indexes on TEXT columns found.")


def post_init_hook(env):
    """Post-installation hook to migrate TEXT to JSONB and create GIN indexes."""
    cr = env.cr

    _logger.info("base_sparse_field_jsonb: Starting post-install migration...")

    # Find all columns that might be serialized fields
    # These are typically named x_custom_json_attrs or similar
    cr.execute(
        """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE column_name LIKE 'x_custom_json%%'
           OR column_name LIKE '%%_json_attrs'
        ORDER BY table_name, column_name
        """
    )
    columns_to_migrate = cr.fetchall()

    migrated_count = 0
    index_count = 0

    for table_name, column_name, data_type in columns_to_migrate:
        current_type = data_type

        # Migrate TEXT to JSONB if needed
        if data_type == "text":
            _logger.info(
                "Migrating %s.%s from TEXT to JSONB...", table_name, column_name
            )
            try:
                # Convert TEXT to JSONB
                # Handle NULL and empty string cases
                # Use sql.Identifier for safe table/column name quoting
                alter_query = sql.SQL(
                    """
                    ALTER TABLE {table}
                    ALTER COLUMN {column}
                    TYPE jsonb
                    USING CASE
                        WHEN {column} IS NULL THEN NULL
                        WHEN {column} = '' THEN '{{}}'::jsonb
                        ELSE {column}::jsonb
                    END
                    """
                ).format(
                    table=sql.Identifier(table_name),
                    column=sql.Identifier(column_name),
                )
                cr.execute(alter_query)
                migrated_count += 1
                current_type = "jsonb"
                _logger.info(
                    "Successfully migrated %s.%s to JSONB", table_name, column_name
                )
            except Psycopg2Error as e:
                _logger.warning(
                    "Could not migrate %s.%s to JSONB: %s", table_name, column_name, e
                )
                # Don't try to create GIN index on TEXT column
                continue

        # Only create GIN index on JSONB columns (never on TEXT)
        if current_type != "jsonb":
            _logger.debug(
                "Skipping GIN index on %s.%s - column is %s, not jsonb",
                table_name,
                column_name,
                current_type,
            )
            continue

        # Create GIN index if not exists
        index_name = f"idx_{table_name}_{column_name}_gin"
        cr.execute(
            """
            SELECT 1 FROM pg_indexes
            WHERE tablename = %s AND indexname = %s
            """,
            (table_name, index_name),
        )
        if not cr.fetchone():
            _logger.info("Creating GIN index on %s.%s...", table_name, column_name)
            try:
                # Use GIN index for JSONB - optimal for key/value lookups
                # Use sql.Identifier for safe table/column/index name quoting
                # Note: Cannot use CONCURRENTLY inside a transaction (post_init_hook)
                create_index_query = sql.SQL(
                    """
                    CREATE INDEX IF NOT EXISTS {index}
                    ON {table} USING GIN ({column})
                    """
                ).format(
                    index=sql.Identifier(index_name),
                    table=sql.Identifier(table_name),
                    column=sql.Identifier(column_name),
                )
                cr.execute(create_index_query)
                index_count += 1
                _logger.info("Created GIN index %s", index_name)
            except Psycopg2Error as e:
                _logger.warning(
                    "Could not create GIN index on %s.%s: %s",
                    table_name,
                    column_name,
                    e,
                )

    _logger.info(
        "base_sparse_field_jsonb: Migration complete. "
        "Migrated %d columns, created %d GIN indexes.",
        migrated_count,
        index_count,
    )
