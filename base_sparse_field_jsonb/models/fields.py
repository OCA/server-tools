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

from psycopg2.extras import Json

from odoo import fields

_logger = logging.getLogger(__name__)


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
