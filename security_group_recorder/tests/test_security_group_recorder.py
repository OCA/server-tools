# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase

from ..models.ir_model import _check_action_profiled_user


class TestSecurityGroupRecorder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.session_model = self.env["res.users.profiler.sessions"]
        self.user_model = self.env["res.users"]
        self.group_model = self.env["res.groups"]
        self.partner_model = self.env["res.partner"]
        self.action_model = self.env["ir.actions.act_window"]
        self.menu_model = self.env["ir.ui.menu"]
        self.group_contact = self.group_model.search(
            [("name", "=", "Contact Creation")]
        )
        self.employee_group = self.env.ref("base.group_user")
        self.active_user = self.user_model.create(
            {
                "name": "admin_user",
                "login": "admin_user",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.ref("base.group_system"),
                            self.group_contact.id,
                            self.employee_group.id,
                        ],
                    )
                ],
            }
        )
        self.action_contacts = self.action_model.create(
            {
                "name": "contacts",
                "res_model": "res.partner",
            }
        )
        self.category_hidden = self.env.ref("base.module_category_hidden")
        self.group = self.group_model.create(
            {
                "name": "GROUP TEST",
                "implied_ids": [(6, 0, [self.employee_group.id])],
                "category_id": self.category_hidden.id,
            }
        )

        self.active_user.groups_id += self.group

        self.menu_parent = self.menu_model.create(
            {
                "name": "Parent Menu",
                "groups_id": [(6, 0, [self.group.id])],
            }
        )
        self.menu_child = self.menu_model.create(
            {
                "name": "Child Menu",
                "parent_id": self.menu_parent.id,
                "action": "ir.actions.act_window,%s" % self.action_contacts.id,
            }
        )
        self.menus = self.menu_parent + self.menu_child

        self.active_session = self.session_model.create(
            {
                "user_id": self.active_user.id,
                "active": True,
            }
        )

    def test_access_rights(self):

        test_partner = self.partner_model.with_user(self.active_user.id).create(
            {"name": "TestContact"}
        )
        test_partner.with_user(self.active_user.id).write(
            {"name": "TestContactModified"}
        )
        test_partner.with_user(self.active_user.id).unlink()

        sessions_active = self.session_model.search([("active", "=", "True")])

        self.assertEqual(1, len(sessions_active))
        self.assertEqual(sessions_active.user_id, self.active_user)

        self.assertGreaterEqual(len(sessions_active.profiled_accesses_ids), 1)

        registered_access_right = self.env["res.users.profiler.accesses"].search(
            [
                ("res_model", "=", "res.partner"),
                ("session_id", "=", self.active_session.id),
            ]
        )

        self.assertTrue(registered_access_right.perm_create)
        self.assertTrue(registered_access_right.perm_write)
        self.assertTrue(registered_access_right.perm_unlink)

        self.assertEqual(registered_access_right.res_model, "res.partner")

    def test_menus_register(self):

        action_dict = {
            "id": self.action_contacts.id,
            "res_model": self.action_contacts.res_model,
        }
        model = action_dict.get("res_model") or ""
        _check_action_profiled_user(
            self.env,
            self.active_user.id,
            self.action_contacts.xml_id,
            action_dict,
            model,
            self.action_contacts.type,
        )

        self.assertEqual(len(self.active_session.profiled_actions_ids), 1)
        self.assertEqual(
            self.active_session.profiled_actions_ids.res_model, "res.partner"
        )
        self.assertEqual(
            self.active_session.profiled_actions_ids.action, self.action_contacts
        )

        self.assertEqual(len(self.active_session.profiled_menus_ids), 2)

        for menu in self.active_session.profiled_menus_ids:
            self.assertTrue(menu in self.menus)
            self.assertTrue(menu not in self.active_session.implied_menus)
