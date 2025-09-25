# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
from odoo.tests import common
from odoo import fields, models



@common.tagged("post_install", "-at_install")
class TestBase(common.TransactionCase):
    def test_num_records_limit(self):
        model_id = self.env["ir.model"]._get("base.limit.records_number.test").id

        self.env["base.limit.records_number"].sudo().create(
            {"name": "Test Rule", "model_id": model_id, "max_records": 1}
        )

        demo_user = self.env.ref("base.user_demo")

        # ok
        self.env["base.limit.records_number.test"].with_user(demo_user).sudo().create(
            {"name": "r1"}
        )

        # limit 1 is reached
        with self.assertRaises(Exception):
            self.env["base.limit.records_number.test"].with_user(demo_user).sudo().create(
                {"name": "r2"}
            )