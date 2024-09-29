# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.modules.module import get_resource_path
from odoo.tests.common import SavepointCase


class TestAccessRights(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user = cls.env["res.users"].create(
            {
                "name": "User",
                "login": "test_user",
                "email": "test_user@example.com",
                "groups_id": [cls.env.ref("base.group_user").id,],  # noqa: E231
            }
        )
        cls.test_admin = cls.env["res.users"].create(
            {
                "name": "Admin",
                "login": "test_admin",
                "email": "test_admin@example.com",
                "groups_id": [
                    cls.env.ref("base.group_system").id,  # noqa: E231
                    cls.env.ref("base_import_module_group.group_module_import").id,
                ],  # noqa: E231
            }
        )

    def test_access_rights(self):
        module_fp = get_resource_path(
            "base_import_module_group", "tests", "data", "base_import_module_group.zip"
        )
        group_xid = "base_import_module_group.group_module_import"

        Users = self.env["res.users"].sudo(self.test_user)
        self.assertFalse(
            Users.has_group(group_xid),
            "The test user shouldn't belong to group_module_import",
        )
        with self.assertRaises(AccessError):
            self.env["ir.module.module"].sudo(self.test_user)._import_module(
                module_fp, "base_import_module_group.zip"
            )

        Users = self.env["res.users"].sudo(self.test_admin)
        self.assertTrue(
            Users.has_group(group_xid),
            "The admin user should belong to group_module_import",
        )
        self.env["ir.module.module"].sudo(self.test_admin)._import_module(
            module_fp, "base_import_module_group.zip"
        )
