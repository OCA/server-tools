# © 2023 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from werkzeug.exceptions import NotFound

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase

from odoo.addons.monitoring.controllers.main import MonitoringHome
from odoo.addons.website.tools import MockRequest

_logger = logging.getLogger(__name__)


class TestMonitoring(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.script = cls.env["monitoring.script"].create(
            {
                "name": "Test Check",
                "snippet": "result = 42",
                "check_type": "lower",
                "warning": 2,
                "critical": 4,
            }
        )

        cls.monitoring = cls.env["monitoring"].create(
            {
                "name": "Test Monitoring",
                "script_ids": [(6, 0, cls.script.ids)],
            }
        )
        cls.controller = MonitoringHome()

    def test_monitoring_script_lower(self):
        self.script.write({"warning": 4, "critical": 4, "check_type": "lower"})
        self.script.validate()
        self.assertEqual(self.script.state, "critical")

        self.script.write({"critical": 44})
        self.script.validate()
        self.assertEqual(self.script.state, "warning")

        self.script.write({"warning": 43})
        self.script.validate()
        self.assertEqual(self.script.state, "ok")

        self.script.snippet = "result = 'invalid'"
        self.script.validate()
        self.assertEqual(self.script.state, "critical")

    def test_monitoring_script_higher(self):
        self.script.write({"warning": 4, "critical": 4, "check_type": "higher"})
        self.script.validate()
        self.assertEqual(self.script.state, "ok")

        self.script.write({"warning": 43})
        self.script.validate()
        self.assertEqual(self.script.state, "warning")

        self.script.write({"critical": 44})
        self.script.validate()
        self.assertEqual(self.script.state, "critical")

        self.script.snippet = "result = 'invalid'"
        self.script.validate()
        self.assertEqual(self.script.state, "critical")

    def test_monitoring_script_boolean(self):
        self.script.write(
            {
                "check_type": "false",
                "snippet": "result = False",
            }
        )
        self.script.validate()
        self.assertEqual(self.script.state, "ok")

        self.script.write({"check_type": "true"})
        self.script.validate()
        self.assertEqual(self.script.state, "critical")

    def test_monitoring_script_validate(self):
        self.assertTrue(self.script.validate())
        self.script.active = False
        self.assertFalse(self.script.validate())

    def test_monitoring(self):
        self.script.write({"warning": 2, "critical": 4})
        self.monitoring.validate()
        self.assertEqual(self.monitoring.state, "critical")

        self.script.state = "warning"
        self.assertEqual(self.monitoring.state, "warning")

        self.script.state = "ok"
        self.assertEqual(self.monitoring.state, "ok")

        self.script.active = False
        self.assertEqual(self.monitoring.state, "unknown")

    def test_monitoring_validation(self):
        # Call all methods and check that there is nothing broken
        self.monitoring.action_validate()
        self.monitoring.cron_validate()

    def test_controller(self):
        with MockRequest(self.env) as request_mock:
            request_mock.not_found = NotFound
            with self.assertRaises(NotFound):
                self.controller.monitoring("invalid")

            response = self.controller.monitoring(self.script.token)
            self.assertEqual(response.status_code, 200)

            response = self.controller.monitoring(self.monitoring.token)
            self.assertEqual(response.status_code, 200)

    def test_formatting_headers(self):
        self.monitoring.output_format = "json"
        self.assertEqual(
            self.monitoring.response_headers().get("Content-Type"),
            "application/json",
        )

        self.monitoring.output_format = "prometheus"
        self.assertEqual(
            self.monitoring.response_headers().get("Content-Type"),
            "text/plain",
        )

        with self.assertRaises(NotImplementedError):
            self.monitoring.output_format = ""
            self.monitoring.response_headers()

    def test_prometheus_configuration(self):
        self.monitoring.output_format = "prometheus"
        self.monitoring._check_prometheus_metric()

        with self.assertRaises(ValidationError):
            self.monitoring.prometheus_label = "invalid!"

        self.monitoring.prometheus_label = "valid"
        with self.assertRaises(ValidationError):
            self.monitoring.prometheus_metric = "invalid!"

    def test_prometheus_formatting(self):
        self.monitoring.output_format = "prometheus"
        result = self.monitoring.validate_and_format()

        metric = self.monitoring.prometheus_metric
        self.assertIn(f"HELP {metric}_value", result)
        self.assertIn(f"TYPE {metric}_value", result)
        self.assertIn(f"HELP {metric}_warning", result)
        self.assertIn(f"TYPE {metric}_warning", result)
        self.assertIn(f"HELP {metric}_critical", result)
        self.assertIn(f"TYPE {metric}_critical", result)

        self.assertEqual(
            self.monitoring.format_prometheus_line(f"{metric}_value", value=1),
            f"{metric}_value 1",
        )

        self.assertEqual(
            self.monitoring.format_prometheus_line(
                f"{metric}_value", value=1, labels={"check": "abc", "test": "def"}
            ),
            '%s_value{check="abc",test="def"} 1' % metric,
        )
