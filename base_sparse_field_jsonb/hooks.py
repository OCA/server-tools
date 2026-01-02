"""Installation hooks for base_sparse_field_jsonb.

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
                _logger.info(
                    "Successfully migrated %s.%s to JSONB", table_name, column_name
                )
            except Psycopg2Error as e:
                _logger.warning(
                    "Could not migrate %s.%s to JSONB: %s", table_name, column_name, e
                )
                cr.rollback()
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
