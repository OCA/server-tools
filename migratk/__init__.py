# -*- coding: utf-8 -*-
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from contextlib import contextmanager
from functools import wraps
from psycopg2 import errorcodes, ProgrammingError
from openerp import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


# TODO Remove when module ends WIP stage
def wip(function):
    """This indicates methods that are currently WIP."""
    @wraps(function)
    def wrapper(*args, **kwargs):
        _logger.warning(
            "BEWARE! You are using an untested function: %s. If you find it "
            "works fine, please remove the `@wip` decorator.",
            function.__name__)
        return function(*args, **kwargs)
    return wrapper


class MigrationException(Exception):
    """Custom exception raised only by the migration toolkit.

    Odoo handles some exceptions like :class:`AttributeError` and
    :class:`psycopg2.OperationalError` in some places of the upper stack. By
    defining a custom class for this toolkit's exceptions, you make Odoo not
    handle them and abort the migration process with a useful error message.
    """
    def __init__(self, old):
        """Create exception and link it to the older one.

        :param Exception old:
            Old exception that was caught before this one.
        """
        _logger.exception(old)
        self.old = old
        super(MigrationException, self).__init__(*old.args)


def manage(function):
    """Run sentences inside a transaction and environment.

    If anything fails inside :param:`function`, all will be rolled back; and
    you have access to an Odoo environment like when using models normally.

    This decorator is prepared to be applied to your ``migrate`` method (the
    required method for all migrations), but if you want to use it in another
    context, at least methods decorated with this must have ``cr`` as their
    first parameter.
    """
    @wraps(function)
    def wrapper(cr, *args, **kwargs):
        try:
            with cr.savepoint():
                with api.Environment.manage():
                    return function(cr, *args, **kwargs)
        except Exception as error:
            raise MigrationException(error)
    return wrapper


class Migrator(object):
    def __init__(self, cr, addon, table_names=None, context=None):
        """Start a migrator instance for a given addon.

        :param openerp.sql_db.Cursor cr:
            Database cursor to use for the migration.

        :param str addon:
            This is the name of the addon where data is attached before running
            the migration.

        :param dict table_names:
            Dictionary mapping model names to table names, such as::

                {"res.partner": "res_partner"}

            Only useful when a model's table **is not** the model's name
            replacing dots by low lines **and** the model name cannot be found
            in Odoo's regitry anymore (maybe because you are deleting it).

        :param dict context:
            Default context for the environment created, in case you need it.
        """
        self.env = api.Environment(cr, SUPERUSER_ID, context or dict())
        self.addon = addon
        self.table_names = table_names or None

    @wip
    @contextmanager
    def _allow_pgcodes(self, *codes):
        """Context manager that will omit specified error codes.

        :param *str codes:
            Undefined amount of error codes found in :mod:`psycopg2.errorcodes`
            that are allowed. Codes can have either 2 characters (indicating an
            error class) or 5 (indicating a concrete error). Any other errors
            will be raised.
        """
        try:
            with self.env.cr.savepoint():
                yield
        except ProgrammingError as error:
            msg = "Code: {code}. Class: {class_}. Error: {error}.".format(
                code=error.pgcode,
                class_=errorcodes.lookup(error.pgcode[:2]),
                error=errorcodes.lookup(error.pgcode))
            if error.pgcode not in codes and error.pgcode[:2] in codes:
                _logger.debug(msg)
            else:
                _logger.exception(msg)
                raise

    def _execute(self, query, params=None, log_exceptions=True):
        """Wrapper that logs before executing.

        Parameters are the same as for :meth:`~.Cursor.execute`, except that
        :param:`log_exceptions` defaults to ``True``.
        """
        _logger.info("Executing query with params %s:\n%s", params, query)
        self.env.cr.execute(query, params, log_exceptions)

    def _fetch_ids(self):
        """Return list of ids from last executed query."""
        return tuple(row["id"] for row in self.env.cr.dictfetchall())

    def _model_id(self, model_name):
        """Get a model's ID in ``ir.model`` table.

        :param str model_name:
            The model name formatted like ``res.partner``.
        """
        self._execute(
            "SELECT id FROM ir_model WHERE model = %s",
            (model_name,))
        return self.env.cr.fetchone()[0]

    def _record_remove(self, model_name, ids, xmlid=True):
        """Remove a record from the database.

        :param str model_name:
            Model name from where to remove the record. E.g. ``res.partner``.

        :param int ids:
            Tuple of IDs of the record to remove.

        :param bool xmlid:
            Wether to remove the XMLID for this record in this addon too.
        """
        table = self._table_name(model_name)
        self._execute("DELETE FROM %s WHERE id IN %%s" % table, (ids,))
        if xmlid:
            self._execute(
                """ DELETE FROM ir_model_data
                    WHERE module = %s AND model = %s AND res_id IN %s
                """,
                (self.addon, model_name, ids))

    def _table_constraint_remove(self, table_name, constraint_name):
        """Remove a constraint from a table.

        :param str table_name:
            Table name for whom to get the constraints. E.g. ``res_partner``.

        :param str constraint_name:
            Constraint to drop.
        """
        self._execute(
            'ALTER TABLE "%s" DROP CONSTRAINT IF EXISTS "%s"' %
            (table_name, constraint_name))

    @wip
    def _table_fk(self, table_name):
        """Get a list of FK constraints pointing to a given DB table.

        .. warning::
            The constraints are found in other tables, but point to
            :param:`table_name`.

        :param str table_name:
            Table name for whom to get the constraints. E.g. ``res_partner``.
        """
        # See http://stackoverflow.com/a/1152321/1468388
        self._execute(
            """ SELECT
                    tc.*,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints AS tc

                    JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name

                    JOIN information_schema.constraint_column_usage AS ccu
                    ON tc.constraint_name = ccu.constraint_name
                WHERE
                    kcu.constraint_type = 'FOREIGN KEY' AND
                    ccu.table_name = %s
            """,
            (table_name,)
        )
        return self.env.cr.dictfetchall()

    def _table_name(self, model_name, lookup=True):
        """Get a table name from a model name.

        This will try to get the table name from :attr:`table_names`, then from
        the ORM, but if it is not found, it will assume that it is the name of
        the model replacing dots by low lines. You will get e.g. get
        ``res_partner`` from ``res.partner``.

        :param str model_name:
            The model name formatted like ``res.partner``.

        :param bool lookup:
            ``False`` to avoid looking for the table name in the ORM. Sometimes
            you only need the computed version, like when using it to search
            for XML IDs.
        """
        if lookup:
            try:
                return self.table_names.get(
                    model_name,
                    self.env[model_name]._table)
            except (AttributeError, KeyError):
                pass
        return model_name.replace(".", "_")

    @wip
    def field_relocate(self, model_name, field_name, destination_addon):
        """Change a field's owner addon.

        This method makes Odoo believe a field now belongs to
        :param:`destination_addon`.

        :param str model_name:
            The model that owns the field. E.g. ``res.partner``.

        :param str old_field:
            The name of the field to migrate. E.g. ``children``.

        :param str destination_addon:
            Name of the addon where the field will be relocated. E.g. ``crm``.
        """
        imd = self.env["ir.model.data"]
        lined = self._table_name(model_name, False)
        filters = [("module", "=", self.addon)]
        update = {"module": destination_addon}
        xmlid_base = "field_%s_%s" % (lined, field_name)

        # Change field's addon
        records = imd.search(
            filters + [("name", "like", xmlid_base + "%")])
        for r in records:
            if r.name in (xmlid_base, "%s_%d" % (xmlid_base, r.res_id)):
                with self._allow_pgcodes():
                    records.write(update)

    @wip
    def field_rename(self, model_name, old_field, new_field):
        """Rename a field.

        The base Odoo ORM already allows you to add the ``oldname`` parameter
        to any field definition to start a deprecation process for the old
        field name. However, in some complex migrations where you need to
        rename it manually, this is your tool.

        :param str model_name:
            The model that owns the field. E.g. ``res.partner``.

        :param str old_field:
            The name of the field before migrating. E.g. ``children``.

        :param str new_field:
            The desired new name for the field. E.g. ``child_ids``.
        """
        imd = self.env["ir.model.data"]
        table = self._table_name(model_name)
        lined = self._table_name(model_name, False)
        filters = [("module", "=", self.addon)]

        # Alter DB structure
        queries = (
            """ALTER TABLE {table}
               DROP CONSTRAINT IF EXISTS {table}_{old_field}_fkey""",
            "ALTER TABLE {table} RENAME COLUMN {old_field} TO {new_fields}",
        )
        for q in queries:
            self._execute(
                q.format(table=table,
                         old_field=old_field,
                         new_field=new_field))

        # Rename field for Odoo
        old_name = "field_%s_%s" % (lined, old_field)
        records = imd.search(filters + [("name", "like", "%s%%" % old_name)])
        for r in records:
            new_name = "field_%s_%s" % (lined, new_field)
            if r.name.endswith("_%d" % r.res_id):
                new_name += "_%d" % r.res_id
            r.write({"name": new_name})

    @wip
    def model_relocate(self, model_name, destination_addon):
        """Change a model's owner addon.

        Models are owned by an addon. That makes Odoo remove the model or
        fields when the addon is removed. This method makes Odoo believe a
        model now belongs to :param:`destination_addon`.

        :param str model_name:
            Model name. E.g. ``res.partner``.

        :param str destination_addon:
            Name of the addon where the model will be relocated. E.g. ``crm``.
        """
        imd = self.env["ir.model.data"]
        lined = self._table_name(model_name, False)
        filters = [("module", "=", self.addon)]
        update = {"module": destination_addon}

        # Change model's addon
        records = imd.search(filters + [("name", "=", "model_%s" % lined)])
        with self._allow_pgcodes():
            records.write(update)

        # Change model's fields' addon
        records = imd.search(filters + [("name", "=", "field_%s_%%" % lined)])
        for r in records:
            with self._allow_pgcodes():
                r.write(update)

    def model_remove(self, model_name, remove_table=True):
        """Remove a model from database.

        :param str model_name:
            Model name. E.g. ``res.partner``.

        :param bool remove_table:
            Specifies wether the database tables should be dropped.
        """
        model_id = self._model_id(model_name)

        # Clean model info for Odoo
        self._execute(
            "SELECT id FROM ir_model_constraint WHERE model = %s",
            (model_id,))
        ids = self._fetch_ids()
        if ids:
            self._record_remove("ir.model.constraint", ids)

        self._execute(
            "SELECT id FROM ir_model_fields WHERE model_id = %s",
            (model_id,))
        ids = self._fetch_ids()
        if ids:
            self._record_remove("ir.model.fields", ids)

        self._record_remove("ir.model", (model_id,))

        # Remove database table
        if remove_table:
            table = self._table_name(model_name)
            self._execute('DROP TABLE IF EXISTS "%s"' % table)
            self._execute('DROP VIEW IF EXISTS "%s"' % table)

    @wip
    def model_rename(self, old_name, new_name):
        """Rename a model.

        :param str old_name:
            The old model name, as currently found in the database. E.g.
            ``res.partner``.

        :param str new_name:
            The new model name. E.g. ``res.partner.new``.
        """
        imd = self.env["ir.model.data"]
        filters = [("module", "=", self.addon)]
        old_lined = self._table_name(old_name, False)
        old_table = self._table_name(old_name)
        new_table = self._table_name(new_name)

        queries = (
            # Rename common constraints
            "ALTER SEQUENCE {old_table}_id_seq RENAME TO {new_table}_id_seq;",
            "ALTER INDEX {old_table}_pkey RENAME TO {new_table}_pkey;",
            """ALTER TABLE {old_table}
               RENAME CONSTRAINT {old_table}_create_uid_fkey
               TO {new_table}_create_uid_fkey;""",
            """ALTER TABLE {old_table}
               RENAME CONSTRAINT {old_table}_write_uid_fkey
               TO {new_table}_write_uid_fkey;""",

            # Rename DB table
            "ALTER TABLE {old_table} RENAME TO {new_table};",
        )
        for q in queries:
            with self._allow_pgcodes():
                self._execute(q.format({"old_table": old_table,
                                        "new_table": new_table}))

        # Rename model for Odoo
        records = imd.search(
            filters + [("name", "=", "model_%s" % old_lined)])
        with self._allow_pgcodes():
            records.write({
                "name": "model_%s" % new_table,
            })

        # Rename model's fields for Odoo
        records = imd.search(
            filters + [("name", "like", "field_%s_%%" % old_lined)])
        with self._allow_pgcodes():
            records.write({
                "name": "field_%s_%%" % new_table,
            })

        # Rename user translations
        records = self.env["ir.translation"].search(
            [("name", "like", "%s,%%" % old_name)])
        for r in records:
            r.name = r.name.replace(old_name, new_name, 1)
