# Copyright 2026 OBS Solutions B.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

"""Tests for JSONB sparse field functionality.

Adapted from Odoo's base_sparse_field tests:
https://github.com/odoo/odoo/blob/19.0/addons/base_sparse_field/tests/test_sparse_fields.py
"""

import json

from odoo import fields, models
from odoo.orm.model_classes import add_to_registry
from odoo.tests import TransactionCase

from ..hooks import drop_gin_indexes_on_text_columns, post_init_hook, pre_init_hook
from ..models.fields import SerializedJsonb


class SparseFieldsTestModel(models.Model):
    """Test model for sparse fields with JSONB storage."""

    _name = "sparse_fields_jsonb.test"
    _description = "Sparse Fields JSONB Test Model"

    data = fields.Serialized()

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

    def test_convert_to_column_update_with_none(self):
        """Test convert_to_column_update with None value."""
        field = SerializedJsonb()
        record = self.env["sparse_fields_jsonb.test"].create({})

        result = field.convert_to_column_update(None, record)
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


class TestHooks(TransactionCase):
    """Test installation hooks functionality."""

    def test_drop_gin_indexes_on_text_columns_no_indexes(self):
        """Test drop_gin_indexes_on_text_columns when no indexes exist."""
        # Should return 0 when no GIN indexes on TEXT columns exist
        count = drop_gin_indexes_on_text_columns(self.env.cr)
        self.assertEqual(count, 0)

    def test_pre_init_hook_runs_without_error(self):
        """Test pre_init_hook executes without errors."""
        # pre_init_hook should run without raising exceptions
        # even when there are no GIN indexes to drop
        pre_init_hook(self.env)

    def test_post_init_hook_runs_without_error(self):
        """Test post_init_hook executes without errors."""
        # post_init_hook should run without raising exceptions
        # even when there are no columns to migrate
        post_init_hook(self.env)

    def test_post_init_hook_with_jsonb_column(self):
        """Test post_init_hook handles existing JSONB columns."""
        # Create a test table with a JSONB column matching the pattern
        self.env.cr.execute(
            """
            CREATE TABLE IF NOT EXISTS test_hook_table (
                id SERIAL PRIMARY KEY,
                x_custom_json_test JSONB
            )
            """
        )

        # Run post_init_hook - should not fail
        post_init_hook(self.env)

        # Check if GIN index was created
        self.env.cr.execute(
            """
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'test_hook_table'
              AND indexname LIKE '%gin%'
            """
        )
        result = self.env.cr.fetchone()
        self.assertIsNotNone(result)

        # Cleanup
        self.env.cr.execute("DROP TABLE IF EXISTS test_hook_table")

    def test_gin_index_creation_on_jsonb(self):
        """Test that GIN indexes can be created on JSONB columns."""
        # Create a test table
        self.env.cr.execute(
            """
            CREATE TABLE IF NOT EXISTS test_gin_jsonb (
                id SERIAL PRIMARY KEY,
                data JSONB
            )
            """
        )

        # Create GIN index
        self.env.cr.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_test_gin_jsonb_data
            ON test_gin_jsonb USING GIN (data)
            """
        )

        # Verify index exists
        self.env.cr.execute(
            """
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'test_gin_jsonb'
              AND indexname = 'idx_test_gin_jsonb_data'
            """
        )
        result = self.env.cr.fetchone()
        self.assertIsNotNone(result)

        # Cleanup
        self.env.cr.execute("DROP TABLE IF EXISTS test_gin_jsonb")


class TestSerializedJsonbField(TransactionCase):
    """Test SerializedJsonb field class properties."""

    def test_field_type(self):
        """Test that SerializedJsonb has correct type."""
        field = SerializedJsonb()
        self.assertEqual(field.type, "serialized")

    def test_field_column_type(self):
        """Test that SerializedJsonb uses JSONB column type."""
        field = SerializedJsonb()
        self.assertEqual(field.column_type, ("jsonb", "jsonb"))

    def test_field_prefetch(self):
        """Test that SerializedJsonb is not prefetched by default."""
        field = SerializedJsonb()
        self.assertFalse(field.prefetch)

    def test_serialized_class_is_replaced(self):
        """Test that fields.Serialized is now SerializedJsonb."""
        self.assertIs(fields.Serialized, SerializedJsonb)
