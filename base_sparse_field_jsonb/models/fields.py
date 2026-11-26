"""Make the Serialized field of base_sparse_field use PostgreSQL JSONB.

The original ``Serialized`` class is patched in place rather than replaced.
Modules like queue_job or server_environment import it directly from
``odoo.addons.base_sparse_field.models.fields``, and they must get the JSONB
column as well. Patching the class also covers field instances that were
created before this module got imported.

A GIN index is only created when the field asks for one with ``index``. It
gets the name Odoo would give to the index of the field, and
``Registry.check_indexes`` is wrapped so Odoo does not replace it with a
btree index, which is of no use on JSONB. Only ``index=True`` is supported,
other index values are handled like ``True``.
"""

import json
import logging

import psycopg2
from psycopg2.extras import Json

from odoo.orm.registry import Registry
from odoo.tools import SQL, sql

from odoo.addons.base_sparse_field.models.fields import Serialized

_logger = logging.getLogger(__name__)
_schema = logging.getLogger("odoo.schema")


def drop_column_indexes(cr, table_name, column_name):
    """Drop the indexes depending on the given column.

    Indexes built for TEXT (trigram, expressions) can not be rebuilt when the
    column type changes, so they have to go before the conversion. Indexes on
    other columns are left untouched.

    :return: the names of the dropped indexes
    """
    cr.execute(
        SQL(
            """
            SELECT DISTINCT i.relname
              FROM pg_depend d
              JOIN pg_class i ON i.oid = d.objid AND i.relkind = 'i'
              JOIN pg_class t ON t.oid = d.refobjid
              JOIN pg_attribute a
                ON a.attrelid = t.oid AND a.attnum = d.refobjsubid
             WHERE d.classid = 'pg_class'::regclass
               AND d.refclassid = 'pg_class'::regclass
               AND t.relname = %s
               AND a.attname = %s
               AND pg_table_is_visible(t.oid)
               AND NOT EXISTS (
                   SELECT 1 FROM pg_constraint c WHERE c.conindid = i.oid
               )
            """,
            table_name,
            column_name,
        )
    )
    index_names = [row[0] for row in cr.fetchall()]
    for index_name in index_names:
        _logger.warning(
            "Dropping index %s on %s.%s to convert its type",
            index_name,
            table_name,
            column_name,
        )
        sql.drop_index(cr, index_name, table_name)
    return index_names


def _dependent_views(cr, table_name, column_name):
    """Return the views and materialized views reading the given column.

    Views built on top of those are included. Each item is
    ``(name, relkind, definition, index definitions)``, in an order that
    recreates them after the views they depend on.
    """
    cr.execute(
        SQL(
            """
            WITH RECURSIVE deps(oid, depth) AS (
                SELECT r.ev_class, 1
                  FROM pg_depend d
                  JOIN pg_rewrite r ON r.oid = d.objid
                  JOIN pg_class t ON t.oid = d.refobjid
                  JOIN pg_attribute a
                    ON a.attrelid = t.oid AND a.attnum = d.refobjsubid
                 WHERE d.classid = 'pg_rewrite'::regclass
                   AND t.relname = %s
                   AND a.attname = %s
                   AND pg_table_is_visible(t.oid)
                   AND r.ev_class <> t.oid
                UNION
                SELECT r.ev_class, deps.depth + 1
                  FROM deps
                  JOIN pg_depend d ON d.refobjid = deps.oid
                  JOIN pg_rewrite r ON r.oid = d.objid
                 WHERE d.classid = 'pg_rewrite'::regclass
                   AND r.ev_class <> deps.oid
            )
            SELECT c.relname, c.relkind, pg_get_viewdef(c.oid),
                   ARRAY(SELECT pg_get_indexdef(i.indexrelid)
                           FROM pg_index i WHERE i.indrelid = c.oid)
              FROM (SELECT oid, max(depth) AS depth FROM deps GROUP BY oid) v
              JOIN pg_class c ON c.oid = v.oid
             ORDER BY v.depth, c.relname
            """,
            table_name,
            column_name,
        )
    )
    return cr.fetchall()


def _view_kind(relkind):
    return SQL("MATERIALIZED VIEW") if relkind == "m" else SQL("VIEW")


def _alter_column_type(cr, table_name, column_name, alter_query):
    """Run ``alter_query`` changing the type of a column.

    PostgreSQL refuses to change the type of a column read by a view. Those
    views are dropped first and recreated from their own definition
    afterwards. A view whose definition does not fit the new type any more is
    left dropped with a warning; the module owning it recreates it when it is
    updated, as Odoo does when it converts a column itself.
    """
    views = _dependent_views(cr, table_name, column_name)
    for name, relkind, _definition, _indexes in reversed(views):
        _logger.info(
            "Dropping %s %s to convert %s.%s, recreated afterwards",
            "materialized view" if relkind == "m" else "view",
            name,
            table_name,
            column_name,
        )
        cr.execute(
            SQL(
                "DROP %s IF EXISTS %s",
                _view_kind(relkind),
                SQL.identifier(name),
            )
        )
    drop_column_indexes(cr, table_name, column_name)
    cr.execute(alter_query)
    for name, relkind, definition, indexes in views:
        try:
            with cr.savepoint(flush=False):
                cr.execute(
                    SQL(
                        "CREATE %s %s AS %s",
                        _view_kind(relkind),
                        SQL.identifier(name),
                        # literal SQL: "%" (LIKE, modulo) is no placeholder
                        SQL(definition.rstrip().rstrip(";").replace("%", "%%")),
                    )
                )
                for index_definition in indexes:
                    cr.execute(SQL(index_definition.replace("%", "%%")))
        except psycopg2.Error as e:
            _logger.warning(
                "Could not recreate %s after converting %s.%s, it is left to"
                " its module to recreate it: %s",
                name,
                table_name,
                column_name,
                e,
            )


def convert_column_to_jsonb(cr, table_name, column_name):
    """Convert a TEXT column holding serialized values to JSONB."""
    _alter_column_type(
        cr,
        table_name,
        column_name,
        SQL(
            """
            ALTER TABLE %(table)s
                ALTER COLUMN %(column)s DROP DEFAULT,
                ALTER COLUMN %(column)s TYPE jsonb
                USING CASE WHEN %(column)s = '' THEN '{}'::jsonb
                           ELSE %(column)s::jsonb END
            """,
            table=SQL.identifier(table_name),
            column=SQL.identifier(column_name),
        ),
    )
    _logger.info("Converted %s.%s to JSONB", table_name, column_name)


def convert_column_to_text(cr, table_name, column_name):
    """Convert a JSONB column holding serialized values back to TEXT."""
    _alter_column_type(
        cr,
        table_name,
        column_name,
        SQL(
            "ALTER TABLE %(table)s ALTER COLUMN %(column)s TYPE text"
            " USING %(column)s::text",
            table=SQL.identifier(table_name),
            column=SQL.identifier(column_name),
        ),
    )
    _logger.info("Converted %s.%s back to TEXT", table_name, column_name)


def update_gin_index(cr, table_name, column_name, index):
    """Create a GIN index on the column when ``index`` is set.

    An existing index with the same name using another method is replaced.
    Like Odoo does for its own indexes, a failure to create the index is
    logged and does not abort the module installation or update.
    """
    if not index:
        return
    index_name = sql.make_index_name(table_name, column_name)
    cr.execute(
        SQL(
            """
            SELECT am.amname
              FROM pg_class i
              JOIN pg_am am ON am.oid = i.relam
             WHERE i.relname = %s AND i.relkind = 'i'
            """,
            index_name,
        )
    )
    row = cr.fetchone()
    if row and row[0] == "gin":
        return
    try:
        with cr.savepoint(flush=False):
            if row:
                sql.drop_index(cr, index_name, table_name)
            sql.create_index(cr, index_name, table_name, [f'"{column_name}"'], "gin")
    except psycopg2.OperationalError:
        _schema.error("Unable to add GIN index %r on %s", index_name, table_name)


def _update_db_column(self, model, column):
    if column and column["udt_name"] == "text":
        convert_column_to_jsonb(model.env.cr, model._table, self.name)
        column.clear()
        return
    super(Serialized, self).update_db_column(model, column)


def _convert_to_column(self, value, record, values=None, validate=True):
    cache_value = self.convert_to_cache(value, record, validate=validate)
    if cache_value is None:
        return None
    return Json(json.loads(cache_value))


def _convert_to_record(self, value, record):
    # psycopg2 returns a dict for JSONB, a string remains possible as long as
    # the column has not been converted yet
    if isinstance(value, dict):
        return value
    return json.loads(value or "{}")


Serialized.column_type = ("jsonb", "jsonb")
Serialized.update_db_column = _update_db_column
Serialized.convert_to_column = _convert_to_column
Serialized.convert_to_column_insert = _convert_to_column
Serialized.convert_to_record = _convert_to_record

_check_indexes = Registry.check_indexes


def check_indexes(self, cr, model_names):
    """Manage the index of serialized fields as a GIN index.

    Odoo creates a btree index for ``index=True``, and replaces an index of
    another method by a btree one. The ``index`` attribute of serialized fields
    is hidden while Odoo checks the indexes.

    This relies on the 19.0 implementation of ``check_indexes``: for a field
    without ``index``, an existing index with the expected name is kept as is
    ("Keep unexpected index"). Check that this still holds when porting the
    module to another series.
    """
    model_names = list(model_names)
    serialized_fields = [
        (model._table, field, field.index)
        for model in map(self.models.get, model_names)
        if model is not None and model._auto and not model._abstract
        for field in model._fields.values()
        if field.type == "serialized" and field.store and field.index
    ]
    for _table, field, index in serialized_fields:
        if index is not True:
            _schema.warning(
                "Index %r on %r is not supported, a GIN index is created instead",
                index,
                field,
            )
        field.index = False
    try:
        _check_indexes(self, cr, model_names)
    finally:
        for _table, field, index in serialized_fields:
            field.index = index
    for table, field, index in serialized_fields:
        update_gin_index(cr, table, field.name, index)


Registry.check_indexes = check_indexes
