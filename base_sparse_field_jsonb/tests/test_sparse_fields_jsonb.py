# Copyright 2026 OBS Solutions B.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

"""Tests for JSONB sparse field functionality.

Adapted from Odoo's base_sparse_field tests:
https://github.com/odoo/odoo/blob/19.0/addons/base_sparse_field/tests/test_sparse_fields.py
"""

import json

from psycopg2.extras import Json

from odoo import fields, models
from odoo.orm.model_classes import add_to_registry
from odoo.tests import TransactionCase
from odoo.tools import SQL, mute_logger

# Imported the way queue_job and server_environment do it
from odoo.addons.base_sparse_field.models.fields import Serialized as DirectSerialized

from ..hooks import post_init_hook, uninstall_hook
from ..models.fields import SerializedJsonb, update_gin_index

_FIELDS_LOGGER = "odoo.addons.base_sparse_field_jsonb.models.fields"
_TABLE = "sparse_fields_jsonb_test"


class SparseFieldsTestModel(models.Model):
    """Test model for sparse fields with JSONB storage."""

    _name = "sparse_fields_jsonb.test"
    _description = "Sparse Fields JSONB Test Model"

    name = fields.Char()
    data = fields.Serialized()
    indexed_data = fields.Serialized(index=True)
    direct_data = DirectSerialized()

    # Sparse fields stored in the 'data' column
    boolean = fields.Boolean(sparse="data")
    integer = fields.Integer(sparse="data")
    float_field = fields.Float(sparse="data")
    char = fields.Char(sparse="data")
    selection = fields.Selection(
        [("one", "One"), ("two", "Two"), ("three", "Three")],
        sparse="data",
    )
    partner = fields.Many2one("res.partner", sparse="data")


class TestSparseFieldsJsonb(TransactionCase):
    """Test sparse fields functionality with JSONB storage."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Register test model dynamically
        add_to_registry(cls.registry, SparseFieldsTestModel)

        test_models = ["sparse_fields_jsonb.test"]
        cls.registry._setup_models__(cls.env.cr, test_models)
        cls.registry.init_models(cls.env.cr, test_models, {"models_to_check": True})

        # Cleanup: remove test model after tests
        for model_name in test_models:
            cls.addClassCleanup(cls.registry.__delitem__, model_name)

    def test_sparse_fields_basic(self):
        """Test basic sparse field operations (adapted from Odoo test)."""
        record = self.env["sparse_fields_jsonb.test"].create({})
        self.assertFalse(record.data)

        partner = self.env.ref("base.main_partner")
        values = [
            ("boolean", True),
            ("integer", 42),
            ("float_field", 3.14),
            ("char", "John"),
            ("selection", "two"),
            ("partner", partner.id),
        ]

        # Test writing values one by one
        for n, (key, val) in enumerate(values):
            record.write({key: val})
            self.assertEqual(record.data, dict(values[: n + 1]))

        # Test reading values back
        for key, val in values[:-1]:
            self.assertEqual(record[key], val)
        self.assertEqual(record.partner, partner)

        # Test clearing values one by one
        for n, (key, _val) in enumerate(values):
            record.write({key: False})
            self.assertEqual(record.data, dict(values[n + 1 :]))

    def test_sparse_fields_reflection(self):
        """Check reflection of sparse fields in ir.model.fields."""
        names = ["boolean", "integer", "float_field", "char", "selection", "partner"]
        domain = [
            ("model", "=", "sparse_fields_jsonb.test"),
            ("name", "in", names),
        ]
        ir_fields = self.env["ir.model.fields"].search(domain)
        self.assertEqual(len(ir_fields), len(names))
        for ir_field in ir_fields:
            self.assertEqual(ir_field.serialization_field_id.name, "data")

    def test_jsonb_column_type(self):
        """Verify that the Serialized field uses JSONB column type."""
        self.env.cr.execute(
            """
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'sparse_fields_jsonb_test'
              AND column_name = 'data'
            """
        )
        result = self.env.cr.fetchone()
        self.assertIsNotNone(result, "Data column should exist in the table")
        # data_type for jsonb in information_schema is 'jsonb'
        self.assertEqual(result[0], "jsonb", "Column should be JSONB type")

    def test_jsonb_storage_format(self):
        """Test that data is properly stored as JSONB in PostgreSQL."""
        record = self.env["sparse_fields_jsonb.test"].create(
            {
                "boolean": True,
                "integer": 100,
                "char": "Test Value",
            }
        )

        # Flush to database before querying with raw SQL
        record.flush_recordset()

        # Query the raw data from the database
        self.env.cr.execute(
            """
            SELECT data, pg_typeof(data)::text
            FROM sparse_fields_jsonb_test
            WHERE id = %s
            """,
            (record.id,),
        )
        result = self.env.cr.fetchone()

        self.assertIsNotNone(result)
        data, data_type = result

        # Verify the type is jsonb
        self.assertEqual(data_type, "jsonb")

        # Verify the data is a dict (psycopg2 automatically converts jsonb to dict)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("boolean"), True)
        self.assertEqual(data.get("integer"), 100)
        self.assertEqual(data.get("char"), "Test Value")

    def test_sparse_field_update(self):
        """Test updating sparse fields correctly updates JSONB data."""
        record = self.env["sparse_fields_jsonb.test"].create(
            {
                "integer": 10,
                "char": "Initial",
            }
        )

        # Verify initial state
        self.assertEqual(record.integer, 10)
        self.assertEqual(record.char, "Initial")

        # Update one field
        record.write({"integer": 20})
        self.assertEqual(record.integer, 20)
        self.assertEqual(record.char, "Initial")  # Should remain unchanged

        # Flush to database before querying with raw SQL
        record.flush_recordset()

        # Verify in database
        self.env.cr.execute(
            """
            SELECT data->>'integer', data->>'char'
            FROM sparse_fields_jsonb_test
            WHERE id = %s
            """,
            (record.id,),
        )
        result = self.env.cr.fetchone()
        self.assertEqual(result[0], "20")  # JSONB ->> returns text
        self.assertEqual(result[1], "Initial")

    def test_empty_sparse_field(self):
        """Test that empty/falsy values are handled correctly."""
        record = self.env["sparse_fields_jsonb.test"].create({})

        # Initially all should be falsy
        self.assertFalse(record.boolean)
        self.assertEqual(record.integer, 0)
        self.assertEqual(record.float_field, 0.0)
        self.assertFalse(record.char)
        self.assertFalse(record.selection)
        self.assertFalse(record.partner)

        # Data should be empty or falsy
        self.assertFalse(record.data)

    def test_many2one_sparse_field(self):
        """Test Many2one sparse field stores ID and returns recordset."""
        partner = self.env["res.partner"].create({"name": "Test Partner"})

        record = self.env["sparse_fields_jsonb.test"].create({"partner": partner.id})

        # Reading should return recordset
        self.assertEqual(record.partner, partner)
        self.assertEqual(record.partner.id, partner.id)

        # Raw data should store the ID
        self.assertEqual(record.data.get("partner"), partner.id)

    def test_selection_sparse_field(self):
        """Test Selection sparse field with valid values."""
        record = self.env["sparse_fields_jsonb.test"].create({"selection": "one"})
        self.assertEqual(record.selection, "one")

        record.write({"selection": "three"})
        self.assertEqual(record.selection, "three")

        # Clear selection
        record.write({"selection": False})
        self.assertFalse(record.selection)

    def test_convert_to_cache_with_dict(self):
        """Test convert_to_cache with dict value returns JSON string."""
        field = SerializedJsonb()
        record = self.env["sparse_fields_jsonb.test"].create({})

        # Dict should be converted to JSON string
        result = field.convert_to_cache({"key": "value"}, record)
        self.assertEqual(result, '{"key": "value"}')

        # Nested dict
        nested = {"level1": {"level2": {"level3": "deep"}}}
        result = field.convert_to_cache(nested, record)
        self.assertEqual(json.loads(result), nested)

    def test_convert_to_cache_with_non_dict(self):
        """Test convert_to_cache with non-dict values."""
        field = SerializedJsonb()
        record = self.env["sparse_fields_jsonb.test"].create({})

        # None should return None
        result = field.convert_to_cache(None, record)
        self.assertIsNone(result)

        # Empty string should return None
        result = field.convert_to_cache("", record)
        self.assertIsNone(result)

        # False should return None
        result = field.convert_to_cache(False, record)
        self.assertIsNone(result)

        # JSON string should pass through
        json_str = '{"existing": "json"}'
        result = field.convert_to_cache(json_str, record)
        self.assertEqual(result, json_str)

    def test_convert_to_record_with_dict(self):
        """Test convert_to_record with dict value (from JSONB)."""
        field = SerializedJsonb()
        record = self.env["sparse_fields_jsonb.test"].create({})

        # Dict should pass through unchanged
        data = {"key": "value", "number": 42}
        result = field.convert_to_record(data, record)
        self.assertEqual(result, data)

    def test_convert_to_record_with_none(self):
        """Test convert_to_record with None returns empty dict."""
        field = SerializedJsonb()
        record = self.env["sparse_fields_jsonb.test"].create({})

        result = field.convert_to_record(None, record)
        self.assertEqual(result, {})

    def test_convert_to_record_with_string(self):
        """Test convert_to_record with string value (fallback for TEXT)."""
        field = SerializedJsonb()
        record = self.env["sparse_fields_jsonb.test"].create({})

        # JSON string should be parsed
        json_str = '{"from": "string"}'
        result = field.convert_to_record(json_str, record)
        self.assertEqual(result, {"from": "string"})

        # Empty string should return empty dict
        result = field.convert_to_record("", record)
        self.assertEqual(result, {})

    def test_convert_to_column_insert_with_none(self):
        """Test convert_to_column_insert with None value."""
        field = SerializedJsonb()
        record = self.env["sparse_fields_jsonb.test"].create({})

        result = field.convert_to_column_insert(None, record)
        self.assertIsNone(result)

    def test_convert_to_column_with_none(self):
        """Test convert_to_column with None value."""
        field = SerializedJsonb()
        record = self.env["sparse_fields_jsonb.test"].create({})

        result = field.convert_to_column(None, record)
        self.assertIsNone(result)

    def test_postgresql_json_containment_operator(self):
        """Test PostgreSQL @> containment operator on JSONB."""
        record = self.env["sparse_fields_jsonb.test"].create(
            {
                "boolean": True,
                "integer": 42,
                "char": "test",
            }
        )
        record.flush_recordset()

        # Test @> containment operator
        self.env.cr.execute(
            """
            SELECT id FROM sparse_fields_jsonb_test
            WHERE data @> %s::jsonb
            """,
            ('{"integer": 42}',),
        )
        result = self.env.cr.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], record.id)

    def test_postgresql_json_key_exists_operator(self):
        """Test PostgreSQL ? key exists operator on JSONB."""
        record = self.env["sparse_fields_jsonb.test"].create(
            {
                "char": "has_char",
            }
        )
        record.flush_recordset()

        # Test ? key exists operator
        self.env.cr.execute(
            """
            SELECT id FROM sparse_fields_jsonb_test
            WHERE data ? 'char'
            """
        )
        results = self.env.cr.fetchall()
        record_ids = [r[0] for r in results]
        self.assertIn(record.id, record_ids)

    def test_postgresql_json_path_operator(self):
        """Test PostgreSQL -> and ->> path operators on JSONB."""
        record = self.env["sparse_fields_jsonb.test"].create(
            {
                "integer": 999,
                "char": "path_test",
            }
        )
        record.flush_recordset()

        # Test -> operator (returns jsonb)
        self.env.cr.execute(
            """
            SELECT data->'integer' FROM sparse_fields_jsonb_test
            WHERE id = %s
            """,
            (record.id,),
        )
        result = self.env.cr.fetchone()
        self.assertEqual(result[0], 999)

        # Test ->> operator (returns text)
        self.env.cr.execute(
            """
            SELECT data->>'char' FROM sparse_fields_jsonb_test
            WHERE id = %s
            """,
            (record.id,),
        )
        result = self.env.cr.fetchone()
        self.assertEqual(result[0], "path_test")

    def test_batch_create_multiple_records(self):
        """Test creating multiple records with sparse fields."""
        records = self.env["sparse_fields_jsonb.test"].create(
            [
                {"integer": 1, "char": "first"},
                {"integer": 2, "char": "second"},
                {"integer": 3, "char": "third"},
            ]
        )

        self.assertEqual(len(records), 3)
        self.assertEqual(records[0].integer, 1)
        self.assertEqual(records[1].integer, 2)
        self.assertEqual(records[2].integer, 3)

    def test_batch_write_multiple_records(self):
        """Test writing to multiple records with sparse fields."""
        records = self.env["sparse_fields_jsonb.test"].create(
            [
                {"integer": 1},
                {"integer": 2},
                {"integer": 3},
            ]
        )

        # Update all records at once
        records.write({"char": "batch_updated"})

        for record in records:
            self.assertEqual(record.char, "batch_updated")

    def test_search_with_sparse_fields(self):
        """Test that records can be searched after sparse field operations."""
        record = self.env["sparse_fields_jsonb.test"].create({"char": "searchable"})

        # Search should work
        found = self.env["sparse_fields_jsonb.test"].search([("id", "=", record.id)])
        self.assertEqual(len(found), 1)
        self.assertEqual(found.char, "searchable")

    def test_copy_record_with_sparse_fields(self):
        """Test copying a record preserves sparse field values."""
        original = self.env["sparse_fields_jsonb.test"].create(
            {
                "boolean": True,
                "integer": 100,
                "char": "original",
            }
        )

        copy = original.copy()

        self.assertEqual(copy.boolean, True)
        self.assertEqual(copy.integer, 100)
        self.assertEqual(copy.char, "original")
        self.assertNotEqual(copy.id, original.id)

    def test_unlink_record_with_sparse_fields(self):
        """Test deleting a record with sparse fields."""
        record = self.env["sparse_fields_jsonb.test"].create({"integer": 42})
        record_id = record.id

        record.unlink()

        # Should not exist anymore
        self.env.cr.execute(
            """
            SELECT id FROM sparse_fields_jsonb_test WHERE id = %s
            """,
            (record_id,),
        )
        self.assertIsNone(self.env.cr.fetchone())

    def test_float_precision_in_sparse_field(self):
        """Test float precision is preserved in JSONB storage."""
        record = self.env["sparse_fields_jsonb.test"].create(
            {"float_field": 3.141592653589793}
        )

        record.flush_recordset()
        record.invalidate_recordset()

        # Re-read from database
        record = self.env["sparse_fields_jsonb.test"].browse(record.id)
        self.assertAlmostEqual(record.float_field, 3.141592653589793, places=10)

    # Schema helpers

    def _column_type(self, column):
        self.env.cr.execute(
            SQL(
                "SELECT udt_name FROM information_schema.columns"
                " WHERE table_name = %s AND column_name = %s",
                _TABLE,
                column,
            )
        )
        return self.env.cr.fetchone()[0]

    def _index_method(self, index_name):
        self.env.cr.execute(
            SQL(
                "SELECT am.amname FROM pg_class i JOIN pg_am am ON am.oid = i.relam"
                " WHERE i.relname = %s AND i.relkind = 'i'",
                index_name,
            )
        )
        row = self.env.cr.fetchone()
        return row and row[0]

    @mute_logger(_FIELDS_LOGGER)
    def _revert_to_text(self, column):
        self.env.flush_all()
        self.env.cr.execute(
            SQL(
                "DROP INDEX IF EXISTS %(index)s;"
                " ALTER TABLE %(table)s ALTER COLUMN %(column)s TYPE text"
                " USING %(column)s::text",
                index=SQL.identifier(f"{_TABLE}__{column}_index"),
                table=SQL.identifier(_TABLE),
                column=SQL.identifier(column),
            )
        )
        self.env.invalidate_all()

    # Direct import

    def test_direct_import_is_patched(self):
        """Serialized imported from base_sparse_field is the patched class."""
        self.assertIs(DirectSerialized, fields.Serialized)
        self.assertIs(DirectSerialized, SerializedJsonb)
        self.assertEqual(self._column_type("direct_data"), "jsonb")

    def test_direct_import_installed_later(self):
        """A TEXT column of a model loaded later is converted by update_db."""
        record = self.env["sparse_fields_jsonb.test"].create(
            {"direct_data": {"key": "value"}}
        )
        self._revert_to_text("direct_data")
        self.assertEqual(self._column_type("direct_data"), "text")

        self.registry.init_models(
            self.env.cr, ["sparse_fields_jsonb.test"], {"models_to_check": True}
        )

        self.assertEqual(self._column_type("direct_data"), "jsonb")
        self.assertEqual(record.direct_data, {"key": "value"})

    # Indexes

    def test_gin_index_only_when_indexed(self):
        """Only serialized fields with index=True get a GIN index."""
        self.assertEqual(self._index_method(f"{_TABLE}__indexed_data_index"), "gin")
        self.assertIsNone(self._index_method(f"{_TABLE}__data_index"))

    def test_gin_index_replaces_btree(self):
        """A btree index left from the TEXT column is replaced by a GIN one."""
        index_name = f"{_TABLE}__indexed_data_index"
        self.env.cr.execute(
            SQL(
                "DROP INDEX %(index)s; CREATE INDEX %(index)s ON %(table)s"
                " USING btree (indexed_data)",
                index=SQL.identifier(index_name),
                table=SQL.identifier(_TABLE),
            )
        )
        self.assertEqual(self._index_method(index_name), "btree")

        update_gin_index(self.env.cr, _TABLE, "indexed_data", True)

        self.assertEqual(self._index_method(index_name), "gin")

    def test_check_indexes_keeps_gin(self):
        """Odoo's index check does not turn the GIN index into a btree one."""
        index_name = f"{_TABLE}__indexed_data_index"
        self.registry.check_indexes(self.env.cr, ["sparse_fields_jsonb.test"])
        self.assertEqual(self._index_method(index_name), "gin")
        field = self.env["sparse_fields_jsonb.test"]._fields["indexed_data"]
        self.assertTrue(field.index)

    def test_check_indexes_creates_gin(self):
        """Odoo's index check creates a missing GIN index."""
        index_name = f"{_TABLE}__indexed_data_index"
        self.env.cr.execute(SQL("DROP INDEX %s", SQL.identifier(index_name)))
        self.registry.check_indexes(self.env.cr, ["sparse_fields_jsonb.test"])
        self.assertEqual(self._index_method(index_name), "gin")

    # Hooks

    def test_post_init_hook_converts_text_column(self):
        """post_init_hook converts serialized columns of installed models."""
        record = self.env["sparse_fields_jsonb.test"].create(
            {"integer": 42, "char": "kept", "indexed_data": {"a": 1}}
        )
        empty = self.env["sparse_fields_jsonb.test"].create({})
        self._revert_to_text("data")
        self._revert_to_text("indexed_data")
        self.env.cr.execute(
            SQL(
                "UPDATE %s SET data = '' WHERE id = %s",
                SQL.identifier(_TABLE),
                empty.id,
            )
        )

        post_init_hook(self.env)

        self.assertEqual(self._column_type("data"), "jsonb")
        self.assertEqual(self._column_type("indexed_data"), "jsonb")
        self.assertEqual(self._index_method(f"{_TABLE}__indexed_data_index"), "gin")
        self.assertEqual(record.integer, 42)
        self.assertEqual(record.char, "kept")
        self.assertEqual(record.indexed_data, {"a": 1})
        self.assertEqual(empty.data, {})

    def test_post_init_hook_keeps_other_indexes(self):
        """Only indexes on the converted column are dropped."""
        self._revert_to_text("data")
        self.env.cr.execute(
            SQL(
                "CREATE INDEX test_data_tsv ON %(table)s"
                " USING gin (to_tsvector('simple', data));"
                " CREATE INDEX test_name_tsv ON %(table)s"
                " USING gin (to_tsvector('simple', name))",
                table=SQL.identifier(_TABLE),
            )
        )

        with mute_logger(_FIELDS_LOGGER):
            post_init_hook(self.env)

        self.assertEqual(self._column_type("data"), "jsonb")
        self.assertIsNone(self._index_method("test_data_tsv"))
        self.assertEqual(self._index_method("test_name_tsv"), "gin")

    def test_uninstall_hook_reverts_to_text(self):
        """uninstall_hook puts the serialized columns back to TEXT."""
        record = self.env["sparse_fields_jsonb.test"].create(
            {"integer": 7, "indexed_data": {"a": 1}}
        )
        self.env.flush_all()

        with mute_logger(_FIELDS_LOGGER):
            uninstall_hook(self.env)

        for column in ("data", "indexed_data", "direct_data"):
            self.assertEqual(self._column_type(column), "text")
        self.assertIsNone(self._index_method(f"{_TABLE}__indexed_data_index"))
        self.env.cr.execute(
            SQL("SELECT data FROM %s WHERE id = %s", SQL.identifier(_TABLE), record.id)
        )
        self.assertEqual(json.loads(self.env.cr.fetchone()[0]), {"integer": 7})


class TestSerializedJsonbField(TransactionCase):
    """Test the patched Serialized field class."""

    def test_field_type(self):
        field = SerializedJsonb()
        self.assertEqual(field.type, "serialized")

    def test_field_column_type(self):
        field = SerializedJsonb()
        self.assertEqual(field.column_type, ("jsonb", "jsonb"))

    def test_field_prefetch(self):
        field = SerializedJsonb()
        self.assertFalse(field.prefetch)

    def test_field_index_default(self):
        """No index unless the field asks for one."""
        self.assertFalse(SerializedJsonb().index)

    def test_convert_to_column_insert_with_dict(self):
        field = SerializedJsonb()
        record = self.env["res.partner"].browse()

        result = field.convert_to_column_insert({"key": "value"}, record)
        self.assertIsInstance(result, Json)

    def test_convert_to_column_with_dict(self):
        field = SerializedJsonb()
        record = self.env["res.partner"].browse()

        result = field.convert_to_column({"key": "value"}, record)
        self.assertIsInstance(result, Json)
