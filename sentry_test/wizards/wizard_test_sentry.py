# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

import requests

from odoo import models

_logger = logging.getLogger(__name__)


class WizardTestSentry(models.Model):
    _name = "wizard.test.sentry"
    _description = "Wizard Test Sentry"

    def test_http_delay(self):
        _logger.info("I am doing some complexe HTTP request")
        requests.get("https://httpbin.org/delay/3")
        return True

    def test_db_delay(self):
        _logger.info("I am doing some complexe SQL request")
        self.env.cr.execute("SELECT PG_SLEEP(5)")

    def test_all(self):
        _logger.info("I am doing everything complexe, simple is hard")
        self.test_http_delay()
        self.test_db_delay()

    def _divide_by_zero(self):
        _logger.info("I am learning math")
        return 1 / 0

    def test_crash(self):
        self._divide_by_zero()

    def test_queue_job(self):
        self.with_delay().test_http_delay()
        self.with_delay().test_db_delay()
        self.with_delay().test_all()
        self.with_delay().test_crash()

    def test_log_error(self):
        _logger.info("I should be in the breadcrum")
        _logger.error("No crash but a log error should raise an event")

    def test_log_warning(self):
        _logger.warning(
            "No crash but a log warning should raise an event dependending "
            "of the configuration."
        )
