# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import requests

from odoo import models


class WizardTestSentry(models.Model):
    _name = "wizard.test.sentry"
    _description = "Wizard Test Sentry"

    def test_http_delay(self):
        requests.get("https://httpbin.org/delay/3")
        return True

    def test_db_delay(self):
        self.env.cr.execute("SELECT PG_SLEEP(5)")

    def test_all(self):
        self.test_http_delay()
        self.test_db_delay()

    def _divide_by_zero(self):
        return 1 / 0

    def test_crash(self):
        self._divide_by_zero()
