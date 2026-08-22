# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

import json

from odoo.tests.common import HttpCase, TransactionCase


class TestORMGraphModel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)

    def test_action_view_ormgraph(self):
        """Test smart button action on ir.model record."""
        action = self.partner_model.action_view_ormgraph()
        self.assertEqual(action.get("type"), "ir.actions.act_url")
        self.assertIn("res.partner", action.get("url", ""))


class TestORMGraphController(HttpCase):
    def setUp(self):
        super().setUp()
        self.authenticate("admin", "admin")

    def test_api_graph_route(self):
        """Test /api/graph HTTP GET endpoint returns valid graph JSON."""
        response = self.url_open("/api/graph")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn("models", data)
        self.assertIn("relationships", data)
        self.assertIn("stats", data)

    def test_api_path_route_valid(self):
        """Test /api/path with valid source and target models."""
        response = self.url_open("/api/path?source=res.partner&target=res.partner")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn("path", data)

    def test_api_path_route_missing_params(self):
        """Test /api/path returns 400 when params are missing."""
        response = self.url_open("/api/path")
        self.assertEqual(response.status_code, 400)

    def test_api_metrics_route(self):
        """Test /api/metrics HTTP GET endpoint returns architecture metrics."""
        response = self.url_open("/api/metrics")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn("total_models", data)
        self.assertIn("total_relationships", data)
        self.assertIn("most_connected", data)

    def test_studio_route(self):
        """Test /ormgraph/studio entrypoint returns HTML page."""
        response = self.url_open("/ormgraph/studio")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("Content-Type", ""))
