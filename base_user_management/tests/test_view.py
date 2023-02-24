from odoo.tests.common import TransactionCase


class ViewTest(TransactionCase):
    def test_other_users_view(self):
        other_user = self.env["res.users"].create({"name": "dennis", "login": "dennis"})
        view = self.ref("base.view_users_form")
        erp_group_id = self.ref("base.group_erp_manager")
        action_id = self.ref("base.action_res_users")
        self.env["res.groups"]._update_user_groups_view()
        res = (
            self.env["res.users"]
            .with_user(other_user)
            .get_view(view_id=view, action_id=action_id)
        )
        self.assertNotIn("sel_groups_%s_" % erp_group_id, res["arch"])

    def test_erp_manager_view(self):
        admin = self.ref("base.user_admin")
        view = self.ref("base.view_users_form")
        erp_group_id = self.ref("base.group_erp_manager")
        action_id = self.ref("base.action_res_users")
        self.env["res.groups"]._update_user_groups_view()
        res = (
            self.env["res.users"]
            .with_user(admin)
            .get_view(view_id=view, action_id=action_id)
        )
        self.assertIn("sel_groups_%s_" % erp_group_id, res["arch"])
