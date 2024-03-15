# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import Form, TransactionCase


class TestRequestCancelConfirm(TransactionCase):
    def setUp(self):
        super(TestRequestCancelConfirm, self).setUp()
        self.request_obj = self.env["request.request"]
        self.request = self.request_obj.create(
            {
                "category_id": self.env.ref(
                    "request_flow.request_category_data_general_request"
                ).id,
                "requested_by": self.env.ref("base.user_admin").id,
                "approver_id": self.env.ref("base.user_admin").id,
            }
        )

    def test_01_cancel_confirm_request(self):
        """Cancel a document, I expect cancel_reason.
        Then, set to draft, I expect cancel_reason is deleted.
        """
        self.request.action_confirm()
        # Click reject, cancel confirm wizard will open. Type in cancel_reason
        res = self.request.action_cancel()
        ctx = res.get("context")
        self.assertEqual(ctx["cancel_method"], "action_cancel")
        self.assertEqual(ctx["default_has_cancel_reason"], "optional")
        wizard = Form(self.env["cancel.confirm"].with_context(ctx))
        wizard.cancel_reason = "Wrong information"
        wiz = wizard.save()
        # Confirm cancel on wizard
        wiz.confirm_cancel()
        self.assertEqual(self.request.cancel_reason, wizard.cancel_reason)
        self.assertEqual(self.request.state, "cancel")
        # Set to draft
        self.request.action_draft()
        self.assertEqual(self.request.cancel_reason, False)
        self.assertEqual(self.request.state, "draft")
