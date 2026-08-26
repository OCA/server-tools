# Copyright 2024 Camptocamp (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo.addons.base.tests.common import BaseCommon

MODULE = "base_force_record_noupdate"


class TestBaseForceRecordNoupdate(BaseCommon):
    def test_00_test_model_create_noupdate_propagation(self):
        # NB: we're only testing models created through UI, the feature is not
        # supported yet for models created by the code itself
        imd = self.env["ir.model.data"].create(
            {
                "module": MODULE,
                "name": "test_ir_model_data_record",
                "model": "x_my.model.test.00",
                "noupdate": False,
            }
        )
        self.env["ir.model"].create(
            {
                "name": "My Model Test 00",
                "state": "manual",
                "model": "x_my.model.test.00",
                "force_noupdate": True,
            }
        )
        self.assertTrue(imd.noupdate)

    def test_01_test_model_write_noupdate_propagation(self):
        my_model = self.env["ir.model"].create(
            {
                "name": "My Model Test 01",
                "state": "manual",
                "model": "x_my.model.test.01",
                "force_noupdate": False,
            }
        )
        imd = self.env["ir.model.data"].create(
            {
                "module": MODULE,
                "name": "test_ir_model_data_record",
                "model": "x_my.model.test.01",
                "noupdate": False,
            }
        )
        my_model.force_noupdate = True
        self.assertTrue(imd.noupdate)

    def test_02_test_model_data_create_noupdate(self):
        self.env["ir.model"].create(
            [
                {
                    "name": f"My Model Test 02.{n}",
                    "state": "manual",
                    "model": f"x_my.model.test.02.{n}",
                    "force_noupdate": force_noupdate,
                }
                for n, force_noupdate in [(1, True), (2, False)]
            ]
        )
        imd1, imd2 = self.env["ir.model.data"].create(
            [
                {
                    "module": MODULE,
                    "name": f"test_ir_model_data_record_{n}",
                    "model": f"x_my.model.test.02.{n}",
                    "noupdate": False,
                }
                for n in (1, 2)
            ]
        )
        self.assertTrue(imd1.noupdate)
        self.assertFalse(imd2.noupdate)
