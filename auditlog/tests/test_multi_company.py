from unittest.mock import patch

from odoo.fields import Command
from odoo.tests.common import TransactionCase

from odoo.addons.base.models.res_users import Groups


class TestMultiCompany(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Disarm any existing auditing rules.
        cls.env["auditlog.rule"].search([]).unlink()
        cls.env["auditlog.log"].search([]).unlink()
        # Set up a group with two share users from different companies
        cls.company1 = cls.env["res.company"].create({"name": "c1"})
        cls.company2 = cls.env["res.company"].create({"name": "c2"})
        cls.group = cls.env["res.groups"].create({"name": "g1", "share": True})
        cls.user1 = cls.env["res.users"].create(
            {
                "name": "u1",
                "login": "u1",
                "groups_id": [Command.set(cls.group.ids)],
                "company_ids": [Command.set(cls.company1.ids)],
                "company_id": cls.company1.id,
            }
        )
        cls.user2 = cls.env["res.users"].create(
            {
                "name": "u2",
                "login": "u2",
                "groups_id": [Command.set(cls.group.ids)],
                "company_ids": [Command.set(cls.company2.ids)],
                "company_id": cls.company2.id,
            }
        )
        # We will test with a user that has access to only one of the companies
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.user_demo.write(
            {
                "company_ids": [Command.set(cls.company2.ids)],
                "company_id": cls.company2.id,
                "groups_id": [Command.link(cls.env.ref("base.group_system").id)],
            }
        )

    def test_group_set_users(self):  # pylint: disable=missing-return
        """Writing x2many values does not wipe values from inaccessible companies."""
        self.assertEqual(
            self.group.users,
            self.user1 + self.user2,
        )
        self.group.invalidate_recordset()
        group_with_user = self.group.with_user(self.user_demo)
        self.assertEqual(group_with_user.users, self.user2)

        # The issue arises when `users` is missing from the cache and is first
        # read as the superuser when fetching the full values for the auditlog.
        # To emulate this, we want the field missing from the cache at the
        # moment of writing. To prevent various overrides from populating the
        # cache even earlier on when fetching other fields we preemptively fill
        # the cache of the other fields.
        #
        # All of this is undermined by res.users's own `write` method which
        # wipes the cache just in time, so we avoid this override with a patch.
        #
        # The issue is reproduceable on the product.template model without this
        # trickery but this module does not depend on the product module so the
        # model is not available.
        self.group.read()
        self.group.invalidate_recordset(["users"])

        def write(self, vals):
            """Avoid the cache invalidation in this particular override.

            With the faulty behaviour, values from all companies are already
            present in the cache at this point, leading to the deletion of the
            value from the company that is inaccessible to the current user.
            """
            return super(Groups, self).write(vals)

        # Do the write.
        with patch.object(Groups, "write", side_effect=write, autospec=True):
            group_with_user.write({"users": [Command.set(self.user2.ids)]})
        self.assertEqual(group_with_user.users, self.user2)
        # Ensure that the users of the other companies are still there.
        self.env.invalidate_all()
        self.assertEqual(
            self.group.users,
            self.user1 + self.user2,
        )

    def test_group_set_users_with_auditlog(self):
        """Repeat the test above with an auditlog on the groups model"""
        rule = (
            self.env["auditlog.rule"]
            .sudo()
            .create(
                {
                    "name": "Test rule for groups",
                    "model_id": self.env["ir.model"]._get("res.groups").id,
                    "log_read": False,
                    "log_create": False,
                    "log_write": True,
                    "log_unlink": False,
                    "log_type": "full",
                    "state": "subscribed",
                }
            )
        )
        try:
            self.test_group_set_users()
        finally:
            rule.unlink()
