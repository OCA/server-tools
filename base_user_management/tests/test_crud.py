from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class CrudTest(TransactionCase):
    def test_disallowed_groups(self):
        user_manager = self.env["res.users"].create(
            {
                "name": "dennis",
                "login": "dennis",
                "groups_id": [
                    Command.set(
                        [
                            self.ref(
                                "base_user_management.group_access_right_security_manage_users"
                            )
                        ]
                    )
                ],
            }
        )

        disallowed_group = self.ref("base.group_erp_manager")

        with self.assertRaises(AccessError):
            self.env["res.users"].with_user(user_manager).create(
                {
                    "name": "hades",
                    "login": "hades",
                    "groups_id": [Command.set([disallowed_group])],
                }
            )
        with self.assertRaises(AccessError):
            created_user = (
                self.env["res.users"]
                .with_user(user_manager)
                .create(
                    {
                        "name": "hades",
                        "login": "hades",
                    }
                )
            )
            created_user.groups_id = [Command.set([disallowed_group])]

        admin = self.ref("base.user_admin")
        self.env["res.users"].with_user(admin).create(
            {
                "name": "hades",
                "login": "hades",
                "groups_id": [Command.set([disallowed_group])],
            }
        )
