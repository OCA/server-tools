# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import json

from odoo.exceptions import UserError

from .common import JsonExportTestCase


class TestJsonExportSchema(JsonExportTestCase):
    # -- Parser tests --

    def test_get_parser(self):
        """Parser resolves from ir.exports and includes 'id' when configured."""
        parser = self.schema._get_parser()
        self.assertIsInstance(parser, list)
        self.assertIn("id", parser)
        self.assertIn("name", parser)
        self.assertIn("email", parser)
        self.assertIn("phone", parser)
        # Relational field should be a tuple
        relational = [item for item in parser if isinstance(item, tuple)]
        self.assertTrue(relational, "Should have at least one relational field")
        country_tuple = relational[0]
        self.assertEqual(country_tuple[0], "country_id")
        self.assertIn("name", country_tuple[1])

    def test_get_parser_without_record_id(self):
        """'id' excluded when include_record_id is False."""
        self.schema.include_record_id = False
        parser = self.schema._get_parser()
        self.assertNotIn("id", parser)

    def test_get_parser_no_exporter(self):
        """Raises UserError when no exporter is set."""
        schema_no_exp = self.env["json.export.schema"].create(
            {
                "name": "No Exporter",
                "model_id": self.partner_model.id,
            }
        )
        with self.assertRaises(UserError):
            schema_no_exp._get_parser()

    # -- Domain tests --

    def test_get_domain_valid(self):
        """Parses a valid domain string."""
        self.schema.domain = "[('active', '=', True)]"
        domain = self.schema._get_domain()
        self.assertEqual(domain, [("active", "=", True)])

    def test_get_domain_empty(self):
        """Returns empty list for default domain."""
        self.schema.domain = "[]"
        self.assertEqual(self.schema._get_domain(), [])

    def test_get_domain_invalid(self):
        """Returns empty list as fallback for invalid syntax."""
        self.schema.domain = "invalid python code"
        self.assertEqual(self.schema._get_domain(), [])

    # -- Record retrieval tests --

    def test_get_records(self):
        """Returns records matching domain with limit."""
        records = self.schema._get_records(limit=1)
        self.assertTrue(len(records) <= 1)

    def test_get_records_with_offset(self):
        """Pagination offset works."""
        all_records = self.schema._get_records(limit=100)
        if len(all_records) >= 2:
            offset_records = self.schema._get_records(limit=100, offset=1)
            self.assertEqual(len(offset_records), len(all_records) - 1)

    def test_get_records_no_limit(self):
        """no_limit=True returns all matching records."""
        records_limited = self.schema._get_records(limit=1)
        records_all = self.schema._get_records(no_limit=True)
        self.assertGreaterEqual(len(records_all), len(records_limited))

    def test_get_records_extra_domain(self):
        """Extra domain filter is applied."""
        records = self.schema._get_records(
            extra_domain=[("name", "=", "Test Partner 1")]
        )
        for rec in records:
            self.assertEqual(rec.name, "Test Partner 1")

    # -- Serialization tests --

    def test_serialize_records(self):
        """Returns list of dicts with expected keys."""
        records = self.schema._get_records(limit=2)
        data = self.schema._serialize_records(records)
        self.assertIsInstance(data, list)
        if data:
            first = data[0]
            self.assertIn("id", first)
            self.assertIn("name", first)

    # -- Preview tests --

    def test_compute_preview_data(self):
        """Preview data computed as valid JSON string."""
        self.schema._compute_preview_data()
        self.assertTrue(self.schema.preview_data)
        parsed = json.loads(self.schema.preview_data)
        self.assertIsInstance(parsed, list)

    def test_compute_preview_data_no_exporter(self):
        """Empty string when no exporter is set."""
        schema_no_exp = self.env["json.export.schema"].create(
            {
                "name": "No Exporter",
                "model_id": self.partner_model.id,
            }
        )
        self.assertFalse(schema_no_exp.preview_data)

    # -- JSON Schema generation tests --

    def test_generate_json_schema(self):
        """Schema has correct draft-07 structure."""
        json_schema = self.schema._generate_json_schema()
        self.assertEqual(
            json_schema["$schema"], "http://json-schema.org/draft-07/schema#"
        )
        self.assertEqual(json_schema["title"], "Test Partners")
        self.assertEqual(json_schema["type"], "object")
        self.assertIn("properties", json_schema)
        self.assertIn("required", json_schema)
        self.assertFalse(json_schema["additionalProperties"])

    def test_json_schema_field_types(self):
        """FIELD_TYPE_MAP entries produce correct JSON schema types."""
        schema = self.schema._generate_json_schema()
        props = schema["properties"]
        # 'name' is Char → string (but may be wrapped in anyOf if nullable)
        name_prop = props.get("name", {})
        if "anyOf" in name_prop:
            types = [t.get("type") for t in name_prop["anyOf"]]
            self.assertIn("string", types)
        else:
            self.assertEqual(name_prop.get("type"), "string")

    def test_json_schema_relational_many2one(self):
        """Many2one with sub-fields → anyOf[object, null]."""
        schema = self.schema._generate_json_schema()
        props = schema["properties"]
        country_prop = props.get("country_id", {})
        self.assertIn("anyOf", country_prop)
        types = [t.get("type") for t in country_prop["anyOf"]]
        self.assertIn("object", types)
        self.assertIn("null", types)

    def test_json_schema_nullable(self):
        """Non-required fields are wrapped in anyOf with null."""
        model = self.env["res.partner"]
        field_obj = model._fields["email"]
        result = self.schema._field_to_schema(field_obj)
        if not field_obj.required:
            self.assertIn("anyOf", result)
            types = [t.get("type") for t in result["anyOf"]]
            self.assertIn("null", types)

    def test_json_schema_selection_enum(self):
        """Selection fields include enum values."""
        model = self.env["res.partner"]
        field_obj = model._fields["type"]
        result = self.schema._field_to_schema(field_obj)
        # Selection field should have enum, possibly wrapped in anyOf
        if "anyOf" in result:
            inner = result["anyOf"][0]
            self.assertIn("enum", inner)
        else:
            self.assertIn("enum", result)

    def test_compute_json_schema(self):
        """Computed json_schema shows the full API response envelope."""
        self.assertTrue(self.schema.json_schema)
        parsed = json.loads(self.schema.json_schema)
        self.assertIn("$schema", parsed)
        # Envelope properties
        props = parsed["properties"]
        self.assertIn("success", props)
        self.assertIn("data", props)
        self.assertIn("pagination", props)
        self.assertIn("meta", props)
        # Record schema nested under data.items
        self.assertEqual(props["data"]["type"], "array")
        self.assertIn("properties", props["data"]["items"])

    # -- Export action tests --

    def test_action_export_json(self):
        """Creates ir.attachment with base64 JSON content."""
        result = self.schema.action_export_json()
        self.assertEqual(result["type"], "ir.actions.act_url")
        self.assertIn("/web/content/", result["url"])

        # Verify attachment exists and content is valid JSON
        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", "json.export.schema"), ("res_id", "=", self.schema.id)]
        )
        self.assertTrue(attachments)
        content = base64.b64decode(attachments[0].datas).decode("utf-8")
        data = json.loads(content)
        self.assertIsInstance(data, list)

    # -- Log tests --

    def test_create_log(self):
        """Creates log entry with correct fields."""
        log = self.schema._create_log(
            "manual",
            "success",
            records_count=5,
            duration_ms=100,
            request_info='{"test": true}',
        )
        self.assertEqual(log.schema_id, self.schema)
        self.assertEqual(log.log_type, "manual")
        self.assertEqual(log.status, "success")
        self.assertEqual(log.records_count, 5)
        self.assertEqual(log.duration_ms, 100)

    def test_action_view_logs(self):
        """Returns correct action dict."""
        result = self.schema.action_view_logs()
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "json.export.log")
        self.assertIn(("schema_id", "=", self.schema.id), result["domain"])

    def test_compute_log_count(self):
        """Log count matches actual log records."""
        self.schema._create_log("manual", "success", 1, 10)
        self.schema._create_log("api", "error", 0, 5)
        self.schema.invalidate_recordset()
        self.assertEqual(self.schema.log_count, 2)

    # -- Query parameter helper tests --

    def test_get_allowed_query_fields(self):
        """Returns correct set of top-level field names from parser."""
        allowed = self.schema._get_allowed_query_fields()
        self.assertIsInstance(allowed, set)
        self.assertIn("id", allowed)
        self.assertIn("name", allowed)
        self.assertIn("email", allowed)
        self.assertIn("phone", allowed)
        self.assertIn("country_id", allowed)

    def test_build_filter_domain_eq(self):
        """Basic eq filter produces correct domain tuple."""
        from werkzeug.datastructures import ImmutableMultiDict

        params = ImmutableMultiDict([("filter[name][eq]", "Test Partner 1")])
        allowed = self.schema._get_allowed_query_fields()
        domain = self.schema._build_filter_domain(params, allowed)
        self.assertEqual(domain, [("name", "=", "Test Partner 1")])

    def test_build_filter_domain_implicit_eq(self):
        """filter[name]=value without operator defaults to eq."""
        from werkzeug.datastructures import ImmutableMultiDict

        params = ImmutableMultiDict([("filter[name]", "Test Partner 1")])
        allowed = self.schema._get_allowed_query_fields()
        domain = self.schema._build_filter_domain(params, allowed)
        self.assertEqual(domain, [("name", "=", "Test Partner 1")])

    def test_build_filter_domain_ilike(self):
        """ilike operator produces correct domain tuple."""
        from werkzeug.datastructures import ImmutableMultiDict

        params = ImmutableMultiDict([("filter[name][ilike]", "test")])
        allowed = self.schema._get_allowed_query_fields()
        domain = self.schema._build_filter_domain(params, allowed)
        self.assertEqual(domain, [("name", "ilike", "test")])

    def test_build_filter_domain_in(self):
        """in operator splits comma values into a list."""
        from werkzeug.datastructures import ImmutableMultiDict

        params = ImmutableMultiDict([("filter[id][in]", "1,2,3")])
        allowed = self.schema._get_allowed_query_fields()
        domain = self.schema._build_filter_domain(params, allowed)
        self.assertEqual(len(domain), 1)
        field, op, value = domain[0]
        self.assertEqual(field, "id")
        self.assertEqual(op, "in")
        self.assertEqual(value, [1, 2, 3])

    def test_build_filter_domain_rejects_unknown_field(self):
        """ValueError raised for field not in parser."""
        from werkzeug.datastructures import ImmutableMultiDict

        params = ImmutableMultiDict([("filter[password][eq]", "secret")])
        allowed = self.schema._get_allowed_query_fields()
        with self.assertRaises(ValueError) as cm:
            self.schema._build_filter_domain(params, allowed)
        self.assertIn("password", str(cm.exception))

    def test_build_filter_domain_rejects_unknown_operator(self):
        """ValueError raised for unknown operator."""
        from werkzeug.datastructures import ImmutableMultiDict

        params = ImmutableMultiDict([("filter[name][regex]", ".*")])
        allowed = self.schema._get_allowed_query_fields()
        with self.assertRaises(ValueError) as cm:
            self.schema._build_filter_domain(params, allowed)
        self.assertIn("regex", str(cm.exception))

    def test_coerce_filter_value_integer(self):
        """Integer field coercion works correctly."""
        value = self.schema._coerce_filter_value("id", "eq", "42")
        self.assertEqual(value, 42)
        self.assertIsInstance(value, int)

    def test_coerce_filter_value_integer_invalid(self):
        """Invalid integer value raises ValueError."""
        with self.assertRaises(ValueError):
            self.schema._coerce_filter_value("id", "eq", "abc")

    def test_coerce_filter_value_boolean(self):
        """Boolean field coercion works correctly."""
        # 'active' is a boolean field on res.partner
        self.assertTrue(self.schema._coerce_single_value("boolean", "true"))
        self.assertFalse(self.schema._coerce_single_value("boolean", "false"))
        self.assertTrue(self.schema._coerce_single_value("boolean", "1"))

    def test_build_sort_order_basic(self):
        """Single field sort produces correct order string."""
        allowed = self.schema._get_allowed_query_fields()
        order = self.schema._build_sort_order("name", allowed)
        self.assertEqual(order, "name asc")

    def test_build_sort_order_descending(self):
        """Descending sort with - prefix works."""
        allowed = self.schema._get_allowed_query_fields()
        order = self.schema._build_sort_order("-name", allowed)
        self.assertEqual(order, "name desc")

    def test_build_sort_order_composite(self):
        """Multiple sort fields produce composite order string."""
        allowed = self.schema._get_allowed_query_fields()
        order = self.schema._build_sort_order("name,-email", allowed)
        self.assertEqual(order, "name asc, email desc")

    def test_build_sort_order_rejects_unknown_field(self):
        """ValueError raised for sort on field not in parser."""
        allowed = self.schema._get_allowed_query_fields()
        with self.assertRaises(ValueError) as cm:
            self.schema._build_sort_order("password", allowed)
        self.assertIn("password", str(cm.exception))

    def test_filter_parser_subset(self):
        """Returns filtered parser with only requested fields."""
        filtered = self.schema._filter_parser("id,name")
        field_names = [item if isinstance(item, str) else item[0] for item in filtered]
        self.assertIn("id", field_names)
        self.assertIn("name", field_names)
        self.assertNotIn("email", field_names)
        self.assertNotIn("phone", field_names)

    def test_filter_parser_relational(self):
        """Relational field keeps its sub-structure in filtered parser."""
        filtered = self.schema._filter_parser("id,country_id")
        relational = [item for item in filtered if isinstance(item, tuple)]
        self.assertTrue(relational)
        self.assertEqual(relational[0][0], "country_id")
        self.assertIn("name", relational[0][1])

    def test_filter_parser_rejects_unknown_field(self):
        """ValueError raised for field not in parser."""
        with self.assertRaises(ValueError) as cm:
            self.schema._filter_parser("id,password")
        self.assertIn("password", str(cm.exception))
