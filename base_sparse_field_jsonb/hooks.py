"""Installation hooks for base_sparse_field_jsonb.

Models loaded after this module convert their serialized columns themselves,
through ``Serialized.update_db``. The post_init_hook takes care of the
serialized fields of modules that were already installed, and the
uninstall_hook puts the columns back to TEXT for base_sparse_field.
"""

import logging

from odoo.tools import SQL

from .models.fields import (
    convert_column_to_jsonb,
    convert_column_to_text,
    update_gin_index,
)

_logger = logging.getLogger(__name__)


def _serialized_columns(env):
    """Yield (table, column, column type, field) for each stored serialized
    field having a column in the database."""
    for model in env.registry.values():
        if not model._auto or model._abstract:
            continue
        fields = [
            field
            for field in model._fields.values()
            if field.type == "serialized" and field.store
        ]
        if not fields:
            continue
        env.cr.execute(
            SQL(
                """
                SELECT column_name, udt_name
                  FROM information_schema.columns
                 WHERE table_schema = current_schema()
                   AND table_name = %s
                   AND column_name IN %s
                """,
                model._table,
                tuple(field.name for field in fields),
            )
        )
        column_types = dict(env.cr.fetchall())
        for field in fields:
            if field.name in column_types:
                yield model._table, field.name, column_types[field.name], field


def post_init_hook(env):
    """Convert the serialized columns of already installed modules."""
    for table, column, column_type, field in list(_serialized_columns(env)):
        if column_type == "text":
            convert_column_to_jsonb(env.cr, table, column)
        update_gin_index(env.cr, table, column, field.index)


def uninstall_hook(env):
    """Put the serialized columns back to TEXT."""
    for table, column, column_type, _field in list(_serialized_columns(env)):
        if column_type == "jsonb":
            convert_column_to_text(env.cr, table, column)
