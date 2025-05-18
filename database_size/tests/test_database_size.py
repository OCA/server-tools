# Copyright 2025 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestDatabaseSize(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")])
        cls.today = fields.Date.context_today(cls.env.user)
        # Remove any data
        cls.env.cr.execute("delete from ir_model_size")

    def test_database_size(self):
        """Size table is populated and reports can be generated"""
        # Remove any data
        self.env.cr.execute("delete from ir_model_size")
        with self.assertRaisesRegex(UserError, "not.*any data"):
            self.env["ir.model.size.report"].search([])

        self.env.ref(
            "database_size.ir_cron_ir_model_size_measure"
        ).ir_actions_server_id.run()

        # Backdate the data set
        self.env.cr.execute(
            """
            update ir_model_size
            set measurement_date = measurement_date - interval '10 days'
            """
        )
        self.env["ir.model.size"].invalidate_model(["measurement_date"])

        # Generate a new set
        self.env.ref(
            "database_size.ir_cron_ir_model_size_measure"
        ).ir_actions_server_id.run()

        # Retrieve the comparison
        report = self.env["ir.model.size.report"].search(
            [
                ("model", "=", "res.partner"),
                ("measurement_date", "=", self.today),
                ("historical_measurement_date", "=", self.today - timedelta(days=10)),
            ]
        )
        self.assertTrue(report)

        # Run the action to open the details
        action = report.action_open_model_sizes()
        partner_sizes = self.env["ir.model.size"].search(
            [("model", "=", "res.partner")]
        )
        self.assertEqual(len(partner_sizes), 2)
        self.assertEqual(
            self.env[action["res_model"]].search(action["domain"]),
            partner_sizes,
        )

        # Test default dates
        report2 = self.env["ir.model.size.report"].search(
            [("model", "=", "res.partner")]
        )
        # Default measurement date is the most recent date
        self.assertEqual(report2.measurement_date, self.today)
        # Default historical measurement date is the most recent date
        # within the last month
        self.assertEqual(
            report2.historical_measurement_date,
            self.today - timedelta(days=10),
        )

        # Test missing data for date
        with self.assertRaisesRegex(UserError, "no data from"):
            self.env["ir.model.size.report"].search(
                [
                    ("model", "=", "res.partner"),
                    (
                        "historical_measurement_date",
                        "=",
                        self.today - timedelta(days=11),
                    ),
                ]
            )

    def test_database_size_report_diff(self):
        """Size report returns the expected values"""
        with self.assertRaisesRegex(UserError, "not.*any data"):
            self.env["ir.model.size.report"].search([])
        self.env.ref(
            "database_size.ir_cron_ir_model_size_measure"
        ).ir_actions_server_id.run()
        self.env["ir.model.size"].flush_model()

        # Forge some data for the partner model
        self.env.cr.execute(
            """
            update ir_model_size set
            total_database_size = coalesce(total_database_size, 0) + 10,
            total_model_size = coalesce(total_model_size, 0) + 5
            where model = 'res.partner' and measurement_date = %(self.today)s
            returning id;
            """,
            {"self.today": self.today},
        )

        # Backdate the data set
        self.env.cr.execute(
            """
            update ir_model_size
            set measurement_date = measurement_date - interval '10 days'
            """
        )

        # Generate a new set
        self.env.ref(
            "database_size.ir_cron_ir_model_size_measure"
        ).ir_actions_server_id.run()
        self.env["ir.model.size"].flush_model()

        # Forge data for the partner model in the latest data set
        self.env.cr.execute(
            """
            update ir_model_size set
            total_database_size = coalesce(total_database_size, 0) + 15,
            total_model_size = coalesce(total_model_size, 0) + 11
            where model = 'res.partner' and measurement_date = %(self.today)s
            returning id;
            """,
            {"self.today": self.today},
        )

        # Retrieve the comparison
        report = self.env["ir.model.size.report"].search(
            [
                ("model", "=", "res.partner"),
                ("measurement_date", "=", self.today),
                ("historical_measurement_date", "=", self.today - timedelta(days=10)),
            ]
        )

        # Size growth is indicated as expected
        self.assertEqual(report.diff_total_database_size, 5)
        self.assertEqual(report.diff_total_model_size, 6)

    def test_database_size_purge(self):
        """Records are purged according to their age"""

        def purge(**args):
            with freeze_time("2025-01-01"):
                self.env["ir.model.size"]._purge()
            self.env["ir.model.size"].flush_model()

        def create(date):
            return self.env["ir.model.size"].create(
                {
                    "model": "__dummy",
                    "measurement_date": date,
                }
            )

        self.env["ir.config_parameter"].set_param("database_size.purge_enable", False)
        self.env["ir.config_parameter"].set_param(
            "database_size.retention_daily", False
        )
        self.env["ir.config_parameter"].set_param(
            "database_size.retention_monthly", False
        )

        record20231201 = create("2023-12-01")
        record20231202 = create("2023-12-02")
        record20240101 = create("2024-01-01")
        record20240102 = create("2024-01-02")
        record20241201 = create("2024-12-01")
        record20241202 = create("2024-12-02")

        # Purging is disabled
        purge()
        self.assertTrue(record20231202.exists())

        # Enable purging
        self.env["ir.config_parameter"].set_param("database_size.purge_enable", True)

        # By default, entries not on the first date of the month
        # and older than a year are purged
        purge()
        self.assertTrue(record20231201.exists())
        self.assertFalse(record20231202.exists())
        self.assertTrue(record20240101.exists())
        self.assertTrue(record20240102.exists())
        self.assertTrue(record20241201.exists())
        self.assertTrue(record20241202.exists())

        self.env["ir.config_parameter"].set_param("database_size.retention_daily", 32)
        purge()
        self.assertTrue(record20231201.exists())
        self.assertTrue(record20240101.exists())
        self.assertFalse(record20240102.exists())
        self.assertTrue(record20241201.exists())
        self.assertTrue(record20241202.exists())

        self.env["ir.config_parameter"].set_param(
            "database_size.retention_monthly", 366
        )
        purge()
        self.assertFalse(record20231201.exists())
        self.assertTrue(record20240101.exists())
        self.assertTrue(record20241201.exists())
        self.assertTrue(record20241202.exists())
