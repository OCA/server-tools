# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests.common import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestJsonExportController(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Create ir.exports + lines for res.partner
        cls.partner_exporter = cls.env["ir.exports"].create(
            {
                "name": "Test Controller Export",
                "resource": "res.partner",
            }
        )
        for field_name in ["name", "email"]:
            cls.env["ir.exports.line"].create(
                {
                    "export_id": cls.partner_exporter.id,
                    "name": field_name,
                }
            )

        # Create schema
        cls.partner_model = cls.env.ref("base.model_res_partner")
        cls.schema = cls.env["json.export.schema"].create(
            {
                "name": "Controller Test Schema",
                "model_id": cls.partner_model.id,
                "exporter_id": cls.partner_exporter.id,
                "domain": "[]",
                "record_limit": 100,
                "include_record_id": True,
            }
        )

        # Create test partner
        cls.env["res.partner"].create(
            {
                "name": "Controller Test Partner",
                "email": "controller@example.com",
            }
        )

        # Endpoint with no auth (paginated)
        cls.endpoint_no_auth = cls.env["json.export.endpoint"].create(
            {
                "name": "No Auth Endpoint",
                "schema_id": cls.schema.id,
                "route_path": "ctrl-test-noauth",
                "auth_type": "none",
                "page_size": 10,
            }
        )

        # Endpoint with API key auth
        cls.endpoint_api_key = cls.env["json.export.endpoint"].create(
            {
                "name": "API Key Endpoint",
                "schema_id": cls.schema.id,
                "route_path": "ctrl-test-apikey",
                "auth_type": "api_key",
                "api_key": "test-api-key-12345",
                "page_size": 10,
            }
        )

        # Endpoint with CORS
        cls.endpoint_cors = cls.env["json.export.endpoint"].create(
            {
                "name": "CORS Endpoint",
                "schema_id": cls.schema.id,
                "route_path": "ctrl-test-cors",
                "auth_type": "none",
                "cors_origin": "*",
                "page_size": 10,
            }
        )

        # Endpoint with no pagination (all records)
        cls.endpoint_no_page = cls.env["json.export.endpoint"].create(
            {
                "name": "No Pagination Endpoint",
                "schema_id": cls.schema.id,
                "route_path": "ctrl-test-nopage",
                "auth_type": "none",
                "paginate": False,
            }
        )

        # Endpoint with query features enabled
        cls.endpoint_query = cls.env["json.export.endpoint"].create(
            {
                "name": "Query Endpoint",
                "schema_id": cls.schema.id,
                "route_path": "ctrl-test-query",
                "auth_type": "none",
                "page_size": 50,
                "allow_filtering": True,
                "allow_sorting": True,
                "allow_field_selection": True,
            }
        )

        # Endpoint with rate limiting
        cls.endpoint_rate_limit = cls.env["json.export.endpoint"].create(
            {
                "name": "Rate Limited Endpoint",
                "schema_id": cls.schema.id,
                "route_path": "ctrl-test-ratelimit",
                "auth_type": "none",
                "page_size": 10,
                "rate_limit": True,
                "rate_limit_count": 3,
                "rate_limit_window": 60,
            }
        )

        # Create additional test partners for query param tests
        cls.env["res.partner"].create(
            {
                "name": "Alpha Query Partner",
                "email": "alpha@query.com",
            }
        )
        cls.env["res.partner"].create(
            {
                "name": "Beta Query Partner",
                "email": "beta@query.com",
            }
        )

    def _get(self, path, headers=None):
        """Helper to perform a GET request."""
        url = "/api/json_export/%s" % path
        return self.url_open(url, headers=headers or {})

    # -- No auth tests --

    def test_export_data_no_auth(self):
        """GET with auth_type=none returns JSON data."""
        response = self._get("ctrl-test-noauth")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("data", data)
        self.assertIsInstance(data["data"], list)

    # -- API key auth tests --

    def test_export_data_api_key_valid(self):
        """GET with correct X-API-Key header succeeds."""
        response = self._get(
            "ctrl-test-apikey",
            headers={"X-API-Key": "test-api-key-12345"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

    def test_export_data_api_key_invalid(self):
        """GET with wrong key returns 401."""
        response = self._get(
            "ctrl-test-apikey",
            headers={"X-API-Key": "wrong-key"},
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data["success"])

    def test_export_data_api_key_missing(self):
        """GET without key returns 401."""
        response = self._get("ctrl-test-apikey")
        self.assertEqual(response.status_code, 401)

    def test_export_data_api_key_query_param_rejected(self):
        """API key via ?api_key= query param is no longer accepted (header only)."""
        response = self.url_open(
            "/api/json_export/ctrl-test-apikey?api_key=test-api-key-12345"
        )
        self.assertEqual(response.status_code, 401)

    # -- Pagination tests --

    def test_export_data_pagination(self):
        """Response has correct pagination metadata with navigation links."""
        response = self._get("ctrl-test-noauth")
        data = response.json()
        self.assertIn("pagination", data)
        pagination = data["pagination"]
        self.assertIn("page", pagination)
        self.assertIn("page_size", pagination)
        self.assertIn("total", pagination)
        self.assertIn("pages", pagination)
        self.assertEqual(pagination["page"], 1)
        self.assertEqual(pagination["page_size"], 10)
        # Navigation links
        self.assertIn("first", pagination)
        self.assertIn("last", pagination)
        self.assertIn("next", pagination)
        self.assertIsNone(pagination["prev"])

    def test_export_data_page_last(self):
        """?page=last jumps to the last page."""
        response = self.url_open("/api/json_export/ctrl-test-noauth?page=last")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        pagination = data["pagination"]
        self.assertEqual(pagination["page"], pagination["pages"])
        self.assertIsNone(pagination["next"])
        self.assertIsNotNone(pagination["prev"])

    def test_export_data_no_pagination(self):
        """Endpoint with paginate=False returns all records at once."""
        response = self._get("ctrl-test-nopage")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        pagination = data["pagination"]
        self.assertEqual(pagination["page"], 1)
        self.assertEqual(pagination["pages"], 1)
        self.assertEqual(pagination["total"], len(data["data"]))
        # No navigation links when pagination is disabled
        self.assertNotIn("next", pagination)
        self.assertNotIn("prev", pagination)

    # -- 404 test --

    def test_export_data_not_found(self):
        """Non-existent path returns 404."""
        response = self._get("nonexistent-path")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data["success"])

    # -- Schema endpoint tests --

    def test_export_schema_endpoint(self):
        """GET .../schema returns full API response schema with envelope."""
        response = self._get("ctrl-test-noauth/schema")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("$schema", data)
        self.assertEqual(data["type"], "object")
        # Full envelope: success, data, pagination, meta
        props = data["properties"]
        self.assertIn("success", props)
        self.assertIn("data", props)
        self.assertIn("pagination", props)
        self.assertIn("meta", props)
        # data.items holds the record schema
        self.assertEqual(props["data"]["type"], "array")
        self.assertIn("properties", props["data"]["items"])
        # Navigation links in pagination
        pag_props = props["pagination"]["properties"]
        self.assertIn("next", pag_props)
        self.assertIn("prev", pag_props)
        self.assertIn("first", pag_props)
        self.assertIn("last", pag_props)

    # -- CORS tests --

    def test_export_data_cors_headers(self):
        """CORS headers present when cors_origin is set."""
        response = self._get("ctrl-test-cors")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")

    # -- Response structure test --

    def test_export_data_response_structure(self):
        """Response has success, data, pagination, meta keys."""
        response = self._get("ctrl-test-noauth")
        data = response.json()
        self.assertIn("success", data)
        self.assertIn("data", data)
        self.assertIn("pagination", data)
        self.assertIn("meta", data)
        meta = data["meta"]
        self.assertIn("schema", meta)
        self.assertIn("model", meta)
        self.assertIn("duration_ms", meta)

    # -- Log creation test --

    def test_export_data_creates_log(self):
        """API call creates a log entry."""
        log_count_before = self.env["json.export.log"].search_count(
            [("schema_id", "=", self.schema.id), ("log_type", "=", "api")]
        )
        self._get("ctrl-test-noauth")
        log_count_after = self.env["json.export.log"].search_count(
            [("schema_id", "=", self.schema.id), ("log_type", "=", "api")]
        )
        self.assertEqual(log_count_after, log_count_before + 1)

    # -- Filtering tests --

    def test_filter_eq(self):
        """Exact match filtering returns only matching records."""
        response = self.url_open(
            "/api/json_export/ctrl-test-query" "?filter[name][eq]=Alpha Query Partner"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        for item in data["data"]:
            self.assertEqual(item["name"], "Alpha Query Partner")

    def test_filter_ilike(self):
        """Case-insensitive search returns matching records."""
        response = self.url_open(
            "/api/json_export/ctrl-test-query" "?filter[name][ilike]=query partner"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["data"]), 2)
        for item in data["data"]:
            self.assertIn("Query Partner", item["name"])

    def test_filter_multiple_and(self):
        """Two filters compose with AND logic."""
        response = self.url_open(
            "/api/json_export/ctrl-test-query"
            "?filter[name][ilike]=query partner"
            "&filter[email][eq]=alpha@query.com"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["name"], "Alpha Query Partner")

    def test_filter_disallowed_field_400(self):
        """Filtering on a field not in the parser returns 400."""
        response = self.url_open(
            "/api/json_export/ctrl-test-query" "?filter[password][eq]=secret"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("password", data["error"]["message"])

    def test_filter_disabled_endpoint_ignores(self):
        """Filter params silently ignored when allow_filtering=False."""
        response = self.url_open(
            "/api/json_export/ctrl-test-noauth" "?filter[name][eq]=NonexistentName"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        # Should return all records, not filtered
        self.assertGreater(len(data["data"]), 0)

    def test_filter_reduces_total_count(self):
        """Pagination total reflects filtered result count."""
        # Unfiltered total
        response_all = self.url_open("/api/json_export/ctrl-test-query")
        total_all = response_all.json()["pagination"]["total"]

        # Filtered total
        response_filtered = self.url_open(
            "/api/json_export/ctrl-test-query" "?filter[name][eq]=Alpha Query Partner"
        )
        total_filtered = response_filtered.json()["pagination"]["total"]
        self.assertLess(total_filtered, total_all)

    # -- Sorting tests --

    def test_sort_ascending(self):
        """sort=name returns records in ascending name order."""
        response = self.url_open("/api/json_export/ctrl-test-query?sort=name")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        names = [item["name"] for item in data["data"]]
        self.assertEqual(names, sorted(names))

    def test_sort_descending(self):
        """-name prefix gives descending order."""
        response = self.url_open("/api/json_export/ctrl-test-query?sort=-name")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        names = [item["name"] for item in data["data"]]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_sort_disabled_endpoint_ignores(self):
        """Sort param silently ignored when allow_sorting=False."""
        response = self.url_open("/api/json_export/ctrl-test-noauth?sort=-name")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

    # -- Field selection tests --

    def test_fields_subset(self):
        """Response items have only requested keys (plus id if in parser)."""
        response = self.url_open("/api/json_export/ctrl-test-query?fields=id,name")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        for item in data["data"]:
            self.assertIn("id", item)
            self.assertIn("name", item)
            self.assertNotIn("email", item)

    def test_fields_invalid_field_400(self):
        """Requesting a field not in the parser returns 400."""
        response = self.url_open("/api/json_export/ctrl-test-query?fields=id,password")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("password", data["error"]["message"])

    def test_fields_disabled_endpoint_ignores(self):
        """Fields param silently ignored when allow_field_selection=False."""
        response = self.url_open("/api/json_export/ctrl-test-noauth?fields=id,name")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        # Should return all fields, not just id and name
        if data["data"]:
            self.assertIn("email", data["data"][0])

    # -- Combined tests --

    def test_combined_filter_sort_fields(self):
        """All three query features work together."""
        response = self.url_open(
            "/api/json_export/ctrl-test-query"
            "?filter[name][ilike]=query partner"
            "&sort=-name"
            "&fields=id,name"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        # Filtered
        for item in data["data"]:
            self.assertIn("Query Partner", item["name"])
        # Sorted descending
        names = [item["name"] for item in data["data"]]
        self.assertEqual(names, sorted(names, reverse=True))
        # Field subset
        for item in data["data"]:
            self.assertNotIn("email", item)

    # -- Rate limiting tests --

    def test_rate_limit_allows_within_limit(self):
        """Requests within the limit succeed."""
        from ..controllers.main import _rate_limit_store

        # Clear any prior state for this endpoint
        keys_to_clear = [
            k for k in _rate_limit_store if k[0] == self.endpoint_rate_limit.id
        ]
        for k in keys_to_clear:
            del _rate_limit_store[k]

        for _ in range(3):
            response = self._get("ctrl-test-ratelimit")
            self.assertEqual(response.status_code, 200)

    def test_rate_limit_returns_429(self):
        """4th request returns 429 with Retry-After header."""
        from ..controllers.main import _rate_limit_store

        # Clear any prior state for this endpoint
        keys_to_clear = [
            k for k in _rate_limit_store if k[0] == self.endpoint_rate_limit.id
        ]
        for k in keys_to_clear:
            del _rate_limit_store[k]

        for _ in range(3):
            self._get("ctrl-test-ratelimit")

        response = self._get("ctrl-test-ratelimit")
        self.assertEqual(response.status_code, 429)
        self.assertIn("Retry-After", response.headers)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], 429)

    # -- Navigation link tests --

    def test_nav_links_preserve_params(self):
        """Filter/sort params survive in pagination links."""
        # Use a small page_size endpoint to ensure multiple pages
        self.endpoint_query.page_size = 1
        response = self.url_open(
            "/api/json_export/ctrl-test-query"
            "?filter[name][ilike]=query partner"
            "&sort=-name"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        pagination = data["pagination"]
        if pagination.get("next"):
            self.assertIn("filter", pagination["next"])
            self.assertIn("sort=-name", pagination["next"])
        if pagination.get("first"):
            self.assertIn("filter", pagination["first"])
        # Reset page_size
        self.endpoint_query.page_size = 50
