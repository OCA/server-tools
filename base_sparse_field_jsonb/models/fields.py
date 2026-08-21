"""Override Serialized field to use PostgreSQL JSONB instead of TEXT.

This module monkey-patches the Serialized field class from base_sparse_field
to use JSONB column type, enabling:
- GIN indexing for fast key/value lookups
- Native PostgreSQL JSON operators for filtering
- Better storage efficiency (binary format)

The change is transparent to existing code - all serialized attributes
automatically benefit from JSONB storage and querying capabilities.
"""

import json
import logging

from psycopg2 import Error as Psycopg2Error
from psycopg2 import sql as psycopg2_sql
from psycopg2.extras import Json

from odoo import fields

_logger = logging.getLogger(__name__)


def _drop_gin_indexes_on_column(cr, table_name, column_name):
    """Drop any GIN indexes on a specific column before type conversion.

    This is critical when converting TEXT columns to JSONB - PostgreSQL
    cannot convert a column that has a GIN index if the source type is TEXT.

    Args:
        cr: Database cursor
        table_name: Name of the table
        column_name: Name of the column

    Returns:
        int: Number of indexes dropped
    """
    # Find GIN indexes on this specific column
    cr.execute(
        """
        SELECT i.relname AS index_name
        FROM pg_index ix
        JOIN pg_class t ON t.oid = ix.indrelid
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_attribute a ON a.attrelid = t.oid
        JOIN pg_am am ON am.oid = i.relam
        WHERE t.relname = %s
          AND a.attname = %s
          AND am.amname = 'gin'
          AND a.attnum = ANY(ix.indkey)
        """,
        (table_name, column_name),
    )
    indexes = cr.fetchall()

    dropped = 0
    for (index_name,) in indexes:
        _logger.warning(
            "Dropping GIN index '%s' on %s.%s before JSONB conversion",
            index_name,
            table_name,
            column_name,
        )
        try:
            drop_query = psycopg2_sql.SQL("DROP INDEX IF EXISTS {index}").format(
                index=psycopg2_sql.Identifier(index_name),
            )
            cr.execute(drop_query)
            dropped += 1
        except Psycopg2Error as e:
            _logger.error("Could not drop GIN index %s: %s", index_name, e)

    return dropped


# Store reference to original Serialized class
_OriginalSerialized = fields.Serialized


class SerializedJsonb(fields.Field):
    """Serialized field using PostgreSQL JSONB for storage.

    This provides the same functionality as the original Serialized field
    but uses JSONB column type instead of TEXT, enabling:
    - GIN index support for fast filtering
    - Native PostgreSQL JSON query operators
    - More efficient binary storage format
    """

    type = "serialized"
    column_type = ("jsonb", "jsonb")  # Use JSONB instead of TEXT

    prefetch = False  # Not prefetched by default (same as original)

    def update_db(self, model, columns):
        """Override to drop GIN indexes on TEXT columns before conversion.

        This is called during _auto_init when the column might need to be
        created or converted. We need to drop any GIN indexes BEFORE
        PostgreSQL tries to convert TEXT to JSONB, as GIN indexes on
        TEXT columns will block the conversion.
        """
        column = columns.get(self.name)
        if column:
            # Column exists - check if it's TEXT with a GIN index
            current_type = column.get("udt_name", "").lower()
            if current_type == "text":
                # Drop GIN indexes before conversion attempt
                _drop_gin_indexes_on_column(
                    model.env.cr,
                    model._table,
                    self.name,
                )

        return super().update_db(model, columns)

    def convert_to_column_insert(self, value, record, values=None, validate=True):
        """Convert value for INSERT - wrap in psycopg2 Json for JSONB."""
        cache_value = self.convert_to_cache(value, record, validate=validate)
        if cache_value is None:
            return None
        # Parse the JSON string back to dict and wrap for JSONB insertion
        return Json(json.loads(cache_value))

    def convert_to_column_update(self, value, record):
        """Convert value for UPDATE - wrap in psycopg2 Json for JSONB."""
        cache_value = self.convert_to_cache(value, record, validate=True)
        if cache_value is None:
            return None
        return Json(json.loads(cache_value))

    def convert_to_cache(self, value, record, validate=True):
        """Convert to cache format: json.dumps(value) or None."""
        # Same as original - cache as JSON string
        return json.dumps(value) if isinstance(value, dict) else (value or None)

    def convert_to_record(self, value, record):
        """Convert from database to record format."""
        if value is None:
            return {}
        # JSONB returns dict directly from psycopg2, TEXT returns string
        if isinstance(value, dict):
            return value
        # Fallback for string (shouldn't happen with JSONB but safe)
        return json.loads(value or "{}")


# Monkey-patch: Replace the Serialized class
fields.Serialized = SerializedJsonb

_logger.info("base_sparse_field_jsonb: Serialized field now uses JSONB column type")
