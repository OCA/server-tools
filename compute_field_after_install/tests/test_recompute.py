# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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

    def test_add_fields(self):
        # Simulate the module installation with a computed field
        records = self.env["res.partner"].search([])
        with patch.dict(
            config.options, {"differ_recomputed_field_size": 1}, clear=True
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
        self.env.cr.execute("UPDATE res_partner SET commercial_company_name=Null")

        partner = self.env.ref("base.res_partner_address_7")
        self.assertFalse(partner.commercial_company_name)

        # Run the cron to process computed field
        self.env["recompute.field"]._run_all()
        self.assertEqual(recompute_field.state, "done")

        # Check that field have been recomputed correctly
        self.assertEqual(partner.commercial_company_name, "Ready Mat")
