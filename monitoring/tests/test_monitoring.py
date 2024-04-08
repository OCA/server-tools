# © 2023 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from werkzeug.exceptions import NotFound

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
            response = self.controller.monitoring("invalid")
            self.assertEqual(response.status_code, 404)

            response = self.controller.monitoring(self.script.token)
            self.assertEqual(response.status_code, 200)

            response = self.controller.monitoring(self.monitoring.token)
            self.assertEqual(response.status_code, 200)
