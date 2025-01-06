# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import Mock, patch
from contextlib import contextmanager

from odoo.tests import TransactionCase
from odoo.tools import config


class TestRecompute(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.env.cr.commit = Mock()

    @contextmanager
    def _count_computes(self, obj, method_name):
        count = {"records": 0, "calls": 0}

        method = getattr(obj.__class__, method_name)

        def _compute(self, *args, **kwargs):
            count["calls"] += 1
            count["records"] += len(self)
            return method(self, *args, **kwargs)

        with patch.object(
            obj.__class__, method_name, side_effect=_compute, autospec=True
        ):
            yield count

    def test_add_fields(self):
        # Simulate the module installation with a computed field
        records = self.env["res.partner"].search([])
        with patch.dict(
            config.options, {"computed_fields_defer_threshold": 1}, clear=True
        ):
            self.env(context={"module": "fake_module"}).add_to_compute(
                records._fields["commercial_company_name"], records
            )

        # Check that a job have been created
        recompute_field = self.env["recompute.field"].search(
            [
                ("model", "=", "res.partner"),
                ("field", "=", "commercial_company_name"),
            ]
        )
        self.assertEqual(recompute_field.state, "todo")

        # Purge field commercial_company_name to simulate
        # the installation of a new field
        self.env.cr.execute("UPDATE res_partner SET commercial_company_name=null")

        partner = self.env.ref("base.res_partner_address_7")
        self.assertFalse(partner.commercial_company_name)

        # Run the cron to process computed field

        with self._count_computes(
            partner,
            "_compute_commercial_company_name",
        ) as computed:
            self.env["recompute.field"]._run_all()
            self.assertEqual(computed["records"], len(records))
            self.assertEqual(computed["calls"], 1)
        self.assertEqual(recompute_field.state, "done")

        # Check that field have been recomputed correctly
        self.assertEqual(partner.commercial_company_name, "Ready Mat")

    def test_add_fields_batch(self):
        # Simulate the module installation with a computed field
        records = self.env["res.partner"].search([])
        with patch.dict(
            config.options,
            {"computed_fields_defer_threshold": 1, "computed_fields_batch_size": 10},
            clear=True,
        ):
            self.env(context={"module": "fake_module"}).add_to_compute(
                records._fields["commercial_company_name"], records
            )

        # Check that a job have been created
        recompute_field = self.env["recompute.field"].search(
            [
                ("model", "=", "res.partner"),
                ("field", "=", "commercial_company_name"),
            ]
        )
        self.assertEqual(recompute_field.state, "todo")

        # Purge field commercial_company_name to simulate
        # the installation of a new field
        self.env.cr.execute("UPDATE res_partner SET commercial_company_name=null")

        partner = self.env.ref("base.res_partner_address_7")
        self.assertFalse(partner.commercial_company_name)

        # Run the cron to process computed field

        with self._count_computes(
            partner,
            "_compute_commercial_company_name",
        ) as computed:
            self.env["recompute.field"]._run_all()
            self.assertEqual(computed["records"], len(records))
            self.assertEqual(computed["calls"], len(records) // 10 + 1)
        self.assertEqual(recompute_field.state, "done")

        # Check that field have been recomputed correctly
        self.assertEqual(partner.commercial_company_name, "Ready Mat")

    def test_add_precompute_fields(self):
        # Precompute fields should not be deferred
        records = self.env["res.partner"].search([])
        with patch.dict(
            config.options, {"computed_fields_defer_threshold": 1}, clear=True
        ):
            self.env(context={"module": "fake_module"}).add_to_compute(
                records._fields["user_id"], records
            )

        # Check that a job have NOT been created
        recompute_field = self.env["recompute.field"].search(
            [
                ("model", "=", "res.partner"),
                ("field", "=", "user_id"),
            ]
        )
        self.assertFalse(recompute_field)

    def test_default_step(self):
        recompute_field = self.env["recompute.field"].create(
            {
                "model": "res.partner",
                "field": "commercial_company_name",
                "state": "todo",
            }
        )
        self.assertEqual(recompute_field.step, 1000)

        with patch.dict(
            config.options, {"computed_fields_batch_size": 2000}, clear=True
        ):
            recompute_field = self.env["recompute.field"].create(
                {
                    "model": "res.partner",
                    "field": "commercial_company_name",
                    "state": "todo",
                }
            )
            self.assertEqual(recompute_field.step, 2000)

            with patch.dict(
                config.options,
                {"computed_fields_batch_size__res_partner": 3000},
                clear=True,
            ):
                recompute_field = self.env["recompute.field"].create(
                    {
                        "model": "res.partner",
                        "field": "commercial_company_name",
                        "state": "todo",
                    }
                )
                self.assertEqual(recompute_field.step, 3000)

                with patch.dict(
                    config.options,
                    {
                        "computed_fields_batch_size__res_partner__commercial_company_name": 4000
                    },
                    clear=True,
                ):
                    recompute_field = self.env["recompute.field"].create(
                        {
                            "model": "res.partner",
                            "field": "commercial_company_name",
                            "state": "todo",
                        }
                    )
                    self.assertEqual(recompute_field.step, 4000)

