# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import math
from contextlib import contextmanager
from unittest.mock import Mock, patch

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
        self.env.invalidate_all()

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
        self.env.invalidate_all()

        partner = self.env.ref("base.res_partner_address_7")
        self.assertFalse(partner.commercial_company_name)

        # Run the cron to process computed field

        with self._count_computes(
            partner,
            "_compute_commercial_company_name",
        ) as computed:
            self.env["recompute.field"]._run_all()
            self.assertEqual(computed["records"], len(records))
            self.assertEqual(computed["calls"], math.ceil(len(records) / 10.0))
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

                option_key = (
                    "computed_fields_batch_size"
                    "__res_partner__commercial_company_name"
                )
                with patch.dict(
                    config.options,
                    {option_key: 4000},
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

    def test_multifields(self):
        if "sale.order" not in self.env:
            self.skipTest("This test requires the sale module to be installed")

        records = self.env["sale.order"].search([])
        original_id_amounts = {
            record.id: (record.amount_untaxed, record.amount_tax, record.amount_total)
            for record in records
        }

        with patch.dict(
            config.options, {"computed_fields_defer_threshold": 1}, clear=True
        ):
            for field in ("amount_untaxed", "amount_tax", "amount_total"):
                self.env(context={"module": "fake_module"}).add_to_compute(
                    records._fields[field], records
                )

        # Check that jobs have been created
        recompute_fields = self.env["recompute.field"].search(
            [
                ("model", "=", "sale.order"),
            ]
        )
        self.assertEqual(len(recompute_fields), 3)
        self.assertEqual(recompute_fields.mapped("state"), ["todo", "todo", "todo"])

        # Purge field commercial_company_name to simulate
        # the installation of a new field
        self.env.cr.execute(
            """
            UPDATE sale_order
            SET amount_untaxed=null, amount_tax=null, amount_total=null
            """
        )
        self.env.invalidate_all()

        for record in records:
            self.assertFalse(record.amount_untaxed)
            self.assertFalse(record.amount_tax)
            self.assertFalse(record.amount_total)

        # Run the cron to process computed field

        with self._count_computes(
            self.env["sale.order"],
            "_compute_amounts",
        ) as computed:
            self.env["recompute.field"]._run_all()
            self.assertEqual(computed["records"], len(records))
            self.assertEqual(computed["calls"], 1)

        self.assertEqual(recompute_fields.mapped("state"), ["done", "done", "done"])

        for record in records:
            self.assertEqual(record.amount_untaxed, original_id_amounts[record.id][0])
            self.assertEqual(record.amount_tax, original_id_amounts[record.id][1])
            self.assertEqual(record.amount_total, original_id_amounts[record.id][2])
