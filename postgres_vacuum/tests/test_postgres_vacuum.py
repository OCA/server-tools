# Copyright 2025 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.tests.common import TransactionCase


class TestPostgresVacuum(TransactionCase):
    def test_vacuum(self):
        with self.assertLogs("odoo.addons.postgres_vacuum", "DEBUG") as logs:
            self.env["ir.cron"]._postgres_vacuum(max_minutes=100, full_vacuum=True)

        self.assertTrue(
            any("vacuum of table res_partner" in log for log in logs.output)
        )

    def test_analyze(self):
        with self.assertLogs("odoo.addons.postgres_vacuum", "DEBUG") as logs:
            self.env["ir.cron"]._postgres_vacuum(max_minutes=100, full_vacuum=False)

        self.assertTrue(
            any("analyze of table res_partner" in log for log in logs.output)
        )
