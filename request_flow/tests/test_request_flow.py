# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import Form, common


class TestRequest(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.category_test = self.env.ref(
            "request_flow.request_category_data_general_request"
        )
        self.demo = self.env.ref("base.user_demo")
        self.admin = self.env.ref("base.user_admin")
        self.admin.write(
            {"groups_id": [(4, self.env.ref("request_flow.group_request_manager").id)]}
        )

    def test_01_request_flow(self):
        res = self.category_test.create_request()
        with Form(self.env[res["res_model"]].with_context(res["context"])) as f:
            f.name = "Test Request"
            f.requested_by = self.demo
        request = f.save()
        # Submit
        self.assertEqual(request.approver_id, self.admin)
        request.action_confirm()
        self.assertEqual(request.state, "pending")
        # Approve by the approver
        with self.assertRaises(UserError):
            request.action_approve()
        request.with_user(self.admin.id).action_approve()
        self.assertEqual(request.state, "approved")
        # Withdraw
        request.with_user(self.admin.id).action_withdraw()
        self.assertEqual(request.state, "pending")
        # Refuse
        request.with_user(self.admin.id).action_refuse()
        self.assertEqual(request.state, "refused")
        # Withdraw Again
        request.with_user(self.admin.id).action_withdraw()
        self.assertEqual(request.state, "pending")
        # Set to Draft by requester
        request.with_user(self.demo.id).action_cancel()
        self.assertEqual(request.state, "cancel")
        request.with_user(self.demo.id).action_draft()
        self.assertEqual(request.state, "draft")

    def test_02_context_overwrite(self):
        self.category_test.context_overwrite = "{'default_amount': 100}"
        res = self.category_test.create_request()
        with Form(self.env[res["res_model"]].with_context(res["context"])) as f:
            f.name = "Test Request"
        request = f.save()
        self.assertEqual(request.amount, 100)
