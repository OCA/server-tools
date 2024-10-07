# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestIrCron(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cron_model = cls.env.ref("base.model_res_partner")
        cls.base_cron_vals = {
            "state": "code",
            "code": "model._test_cron_method()",
            "model_id": cls.cron_model.id,
            "model_name": "res.partner",
            "user_id": cls.env.uid,
            "active": True,
            "interval_number": 1,
            "interval_type": "days",
            "nextcall": fields.Datetime.now() + timedelta(hours=1),
            "lastcall": False,
            "priority": 5,
        }
        cls.cron1 = cls.env["ir.cron"].create(
            {
                **cls.base_cron_vals,
                "name": "Test Cron 1",
            }
        )
        cls.cron2 = cls.env["ir.cron"].create(
            {
                **cls.base_cron_vals,
                "name": "Test Cron 2",
            }
        )

    def test_check_auto_exclusion_self_reference(self):
        """Test that a cron job cannot be mutually exclusive with itself"""
        with self.assertRaises(ValidationError):
            self.cron1.mutually_exclusive_cron_ids = self.cron1.ids

    def test_mutually_exclusive_cron_assignment(self):
        """Test normal assignment of mutually exclusive crons"""
        self.cron1.mutually_exclusive_cron_ids = self.cron2
        self.assertEqual(len(self.cron1.mutually_exclusive_cron_ids), 1)
        self.assertEqual(self.cron1.mutually_exclusive_cron_ids, self.cron2)
