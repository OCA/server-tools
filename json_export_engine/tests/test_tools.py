# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import unittest

from odoo.addons.json_export_engine.tools.resolver import IrExportsResolver
from odoo.addons.json_export_engine.tools.serializer import JsonExportSerializer

from .common import JsonExportTestCase


class TestIrExportsResolver(unittest.TestCase):
    """Pure unit tests for IrExportsResolver (no database needed)."""

    def test_resolve_simple_fields(self):
        """Simple dict fields resolve to strings."""
        parser = {"fields": [{"name": "name"}, {"name": "email"}]}
        result = IrExportsResolver(parser).resolved_parser
        self.assertEqual(result, ["name", "email"])

    def test_resolve_relational_fields(self):
        """Nested tuple fields resolve to (name, [sub_fields])."""
        parser = {
            "fields": [
                ({"name": "categ_id"}, [{"name": "name"}, {"name": "id"}]),
            ]
        }
        result = IrExportsResolver(parser).resolved_parser
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], tuple)
        self.assertEqual(result[0][0], "categ_id")
        self.assertEqual(result[0][1], ["name", "id"])

    def test_resolve_mixed_fields(self):
        """Mix of simple and relational fields."""
        parser = {
            "fields": [
                {"name": "name"},
                ({"name": "country_id"}, [{"name": "name"}, {"name": "code"}]),
                {"name": "phone"},
            ]
        }
        result = IrExportsResolver(parser).resolved_parser
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "name")
        self.assertIsInstance(result[1], tuple)
        self.assertEqual(result[1][0], "country_id")
        self.assertEqual(result[2], "phone")

    def test_resolve_deep_nesting(self):
        """Multi-level nested relations."""
        parser = {
            "fields": [
                (
                    {"name": "partner_id"},
                    [
                        {"name": "name"},
                        ({"name": "country_id"}, [{"name": "name"}]),
                    ],
                ),
            ]
        }
        result = IrExportsResolver(parser).resolved_parser
        self.assertEqual(len(result), 1)
        partner_tuple = result[0]
        self.assertEqual(partner_tuple[0], "partner_id")
        sub_fields = partner_tuple[1]
        self.assertEqual(sub_fields[0], "name")
        self.assertIsInstance(sub_fields[1], tuple)
        self.assertEqual(sub_fields[1][0], "country_id")

    def test_resolve_empty(self):
        """Empty input returns empty list."""
        self.assertEqual(IrExportsResolver({}).resolved_parser, [])
        self.assertEqual(IrExportsResolver({"fields": []}).resolved_parser, [])

    def test_resolve_no_fields_key(self):
        """Missing 'fields' key returns empty list."""
        self.assertEqual(IrExportsResolver({"other": "data"}).resolved_parser, [])

    def test_resolve_broken_tuple(self):
        """Broken tuple structure is filtered out."""
        parser = {
            "fields": [
                {"name": "name"},
                ("not_a_dict", [{"name": "name"}]),
            ]
        }
        result = IrExportsResolver(parser).resolved_parser
        # The broken tuple should be filtered out (empty list result)
        self.assertEqual(result, ["name"])


class TestJsonExportSerializer(JsonExportTestCase):
    """Integration tests for JsonExportSerializer (needs database for jsonify)."""

    def test_serialize_single_record(self):
        """Serializes a single record into a dict."""
        parser = self.schema._get_parser()
        serializer = JsonExportSerializer(parser)
        result = serializer.serialize(self.partner1)
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "Test Partner 1")

    def test_serialize_many_records(self):
        """Serializes multiple records into a list of dicts."""
        parser = self.schema._get_parser()
        serializer = JsonExportSerializer(parser)
        records = self.partner1 | self.partner2
        result = serializer.serialize_many(records)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        names = [item["name"] for item in result]
        self.assertIn("Test Partner 1", names)
        self.assertIn("Test Partner 2", names)

    def test_process_binary_values(self):
        """bytes values are converted to base64 strings."""
        serializer = JsonExportSerializer([])
        data = {"field": b"hello world"}
        result = serializer._process_values(data)
        expected = base64.b64encode(b"hello world").decode("utf-8")
        self.assertEqual(result["field"], expected)

    def test_process_nested_dicts(self):
        """Nested dicts are recursively processed."""
        serializer = JsonExportSerializer([])
        data = {
            "outer": {
                "inner_bytes": b"nested",
                "inner_str": "keep",
            }
        }
        result = serializer._process_values(data)
        expected = base64.b64encode(b"nested").decode("utf-8")
        self.assertEqual(result["outer"]["inner_bytes"], expected)
        self.assertEqual(result["outer"]["inner_str"], "keep")

    def test_process_nested_lists(self):
        """Lists of dicts are recursively processed."""
        serializer = JsonExportSerializer([])
        data = {
            "items": [
                {"val": b"bytes1"},
                {"val": "string"},
            ]
        }
        result = serializer._process_values(data)
        expected = base64.b64encode(b"bytes1").decode("utf-8")
        self.assertEqual(result["items"][0]["val"], expected)
        self.assertEqual(result["items"][1]["val"], "string")
