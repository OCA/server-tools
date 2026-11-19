# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import re

from psycopg2.extensions import AsIs, QuotedString

from odoo import fields
from odoo.fields import resolve_mro
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)


class Searchable(fields.Field):
    type = "tsvector"
    column_type = ("tsvector", "tsvector")
    readonly = True
    copy = False
    fields = None
    dictionary = "english"

    def _get_attrs(self, model, name):
        attrs = super()._get_attrs(model, name)
        attrs.pop("fields_add", None)
        return attrs

    def _setup_attrs(self, model, name):
        super()._setup_attrs(model, name)

        # Set up fields (with fields and fields_add)
        values = None
        for field in reversed(resolve_mro(model, name, self._can_setup_from)):
            if "fields" in field.args:
                fields = field.args["fields"]
                if not isinstance(fields, dict) or not fields:
                    raise ValueError(
                        "%s: fields=%r must be a dict of field name/weight pairs"
                        % (self, fields)
                    )
                if values is not None and values != fields:
                    _logger.warning(
                        "%s: fields=%r overrides existing fields; use fields_add instead",
                        self,
                        fields,
                    )
                values = {**fields}

            if "fields_add" in field.args:
                fields_add = field.args["fields_add"]
                assert isinstance(
                    fields_add, dict
                ), "%s: fields_add=%r must be a dict" % (self, fields_add)
                assert (
                    values is not None
                ), "%s: fields_add=%r on no defined fields %r" % (
                    self,
                    fields_add,
                    self.fields,
                )

                values = {**values, **fields_add}

        if values is not None:
            self.fields = {key: val for key, val in values.items() if val is not None}

        available_languages = self._fetch_languages(model)
        if self.dictionary not in available_languages:
            _logger.warning(
                f"Dictionary '{self.dictionary}' not found, falling back to 'simple'"
            )
            self.dictionary = "simple"

    def _fetch_definition(self, model):
        """Fetch the definition of the tsvector column from the database."""
        cr = model._cr
        cr.execute(
            "SELECT pg_get_expr(d.adbin, d.adrelid) "
            "FROM pg_attribute a JOIN pg_attrdef d ON "
            "a.attrelid = d.adrelid AND a.attnum = d.adnum "
            "WHERE a.attname = %s AND d.adrelid = %s::regclass",
            (self.name, model._table),
        )
        result = cr.fetchone()
        return result[0] if result else None

    def _fetch_languages(self, model):
        """Fetch the available languages from the database."""
        cr = model._cr
        cr.execute("SELECT cfgname FROM pg_ts_config")
        return [row[0] for row in cr.fetchall()]

    def _create_column(self, model):
        """Create the tsvector column in the database."""
        model._cr.execute(
            f"ALTER TABLE {model._table} ADD COLUMN {self.name} tsvector"
            + (
                f" GENERATED ALWAYS AS ({self.get_vector_def(model)}) STORED"
                if not self.compute
                else ""
            ),
        )

    def _drop_column(self, model):
        """Drop the tsvector column from the database."""
        model._cr.execute(
            f"ALTER TABLE {model._table} DROP COLUMN IF EXISTS {self.name}",
        )

    def _create_index(self, model):
        """Create the index on the tsvector column."""
        index_name = f"{model._table}_{self.name}_index"
        model._cr.execute(
            f"CREATE INDEX IF NOT EXISTS {index_name} "
            f"ON {model._table} USING GIN ({self.name})",
        )

    def _should_drop_column(self, model, column):
        # Drop column if it exists and has the wrong type
        if column["udt_name"] != self.column_type[0]:
            return True

        # Get the current vector expression
        definition = self._fetch_definition(model)
        if not definition:
            if not self.compute:
                _logger.warning(
                    f"Recreating column {self.name} for model {model._name} "
                    f"since it does not have an expression and compute is disabled"
                )
                return True
            return False

        if definition and self.compute:
            _logger.warning(
                f"Recreating column {self.name} for model {model._name} "
                f"since it has an expression and compute is enabled"
            )
            return True

        existing_fields = self.get_weighted_field_from_def(definition)
        language = self.get_language_from_def(definition)

        if existing_fields != self.fields:
            _logger.info(
                f"Recreating column {self.name} for model {model._name} "
                f"following field changes {existing_fields} -> {self.fields}"
            )
            return True
        if language != self.dictionary:
            _logger.info(
                f"Recreating column {self.name} for model {model._name} "
                f"following language change {language} -> {self.dictionary}"
            )
            return True

    def update_db_column(self, model, column):
        if column:
            if self._should_drop_column(model, column):
                self._drop_column(model)
                column = None

        # Add generated column
        if not column:
            self._create_column(model)

        self._create_index(model)

    def get_weighted_field_def(self, field, weight, raw=False):
        """Return the weighted field definition for the tsvector column."""
        if not raw:
            field = f"coalesce({field}, '')"
        return (
            f"setweight(to_tsvector({self.dictionary!r}::regconfig, "  # noqa:E231
            f"{field}), '{weight}')"
        )

    def get_weighted_field_from_def(self, definition):
        """Return the weighted field definition from the tsvector column definition."""
        existing_fields = {}
        for field, weight in re.findall(
            r"setweight\(to_tsvector\('\w+'(?:::[^,]+)?, \(?COALESCE\((.+?)"
            r", ''(?:::[^)]+)?\)\)?(?:::[^)]+)?\), '(\w+)'(?:::[^)]+)?",
            definition,
        ):
            existing_fields[field] = weight
        return existing_fields

    def get_language_from_def(self, definition):
        """Return the language from the tsvector column definition."""
        match = re.search(r"to_tsvector\('(\w+)'", definition)
        return match.group(1) if match else None

    def get_vector_def(self, model):
        """Return the vector definition for the tsvector column."""
        return " || ".join(
            [
                self.get_weighted_field_def(field, weight)
                for field, weight in self.fields.items()
            ]
        )

    def _convert_value(self, record, field_name, value):
        field = record._fields.get(field_name)
        if field:
            value = field.convert_to_write(value, record)
            value = field.convert_to_column(value, record)
        # If no field found, assume dynamic string value
        value = QuotedString(value)
        value.encoding = "utf-8"
        value = pycompat.to_text(value.getquoted())
        return value

    def _dict_to_tsvector(self, dct, record):
        return AsIs(
            " || ".join(
                [
                    self.get_weighted_field_def(
                        self._convert_value(record, field, value),
                        self.fields[field],
                        True,
                    )
                    for field, value in dct.items()
                    if field in self.fields and value
                ]
            )
        )

    def convert_to_column(self, value, record, values=None, validate=True):
        if isinstance(value, dict):
            return self._dict_to_tsvector(value, record)
        return super().convert_to_column(value, record, values, validate)


fields.Searchable = Searchable
