# -*- coding: utf-8 -*-
"""Tests for audit menu access (TransientModel) actions."""
import uuid

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo import Command


@tagged("audit_models", "audit_model_access_control")
class TestAuditMenuAccessControl(TransactionCase):
    """Tests for `audit.menu.access.control` (wizards/audit_menu_access_control)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Access = cls.env["audit.menu.access.control"]
        cls.admin_user = cls.env.ref("base.user_admin")
        cls.inspector = cls.env["audit.inspector"].create({"name": "IC Access"})

    def _internal_user(self):
        """Non-admin user for access checks (Odoo 19 ``res.users`` create rules vary by edition)."""
        template = self.env.ref("base.default_user", raise_if_not_found=False)
        if not template:
            self.skipTest(
                "base.default_user template is not available in this database"
            )
        suffix = uuid.uuid4().hex
        return template.sudo().copy(
            {
                "name": f"Audit access test {suffix}",
                "login": f"audit_access_{suffix}@test.local",
                "password": "audit-access-test",
            }
        )

    def test_check_user_access_admin(self):
        user, allowed = self.Access.with_user(self.admin_user).check_user_access()
        self.assertTrue(allowed)
        self.assertEqual(user, self.admin_user)

    def test_check_user_access_unknown_user_denied(self):
        bogus_id = self.env["res.users"].search([], order="id desc", limit=1).id + 9
        internal = self._internal_user()
        user, allowed = self.Access.with_user(internal).check_user_access(
            user_id=bogus_id
        )
        self.assertFalse(allowed)
        self.assertIsNone(user)

    def test_get_team_member_ids_includes_members_and_leaders(self):
        inspector_1 = self.env["audit.inspector"].create({"name": "Inspector_Gadget"})
        inspector_2 = self.env["audit.inspector"].create({"name": "Inspector_Wallace"})
        team_leader = self.env["audit.inspector"].create({"name": "Team_Leader"})

        # Create the team
        team = self.env["audit.team"].create(
            {
                "name": "Access Team",
                "team_member_ids": [Command.set((inspector_1 | inspector_2).ids)],
                "team_leader_ids": [Command.set(team_leader.ids)],
            }
        )

        # Check the team leader is in fact the team leader
        self.assertIn(team_leader.id, [team.team_leader_ids.id])
        # Check the team members are in fact inspectors 1 & 2
        self.assertEqual(
            [inspector_1.id, inspector_2.id],
            [member.id for member in team.team_member_ids],
        )

    def test_build_standard_action_denied_returns_notification(self):
        bogus_id = self.env["res.users"].search([], order="id desc", limit=1).id + 99999
        internal = self._internal_user()
        action = self.Access.with_user(internal)._build_standard_action(
            user_id=bogus_id,
            name="X",
            res_model="audit.team",
            domain_type="team",
        )
        self.assertEqual(action.get("type"), "ir.actions.client")
        self.assertEqual(action.get("tag"), "display_notification")

    def test_inspectors_menu_action_admin_returns_window_action(self):
        action = self.Access.with_user(self.admin_user).inspectors_menu_action()
        self.assertEqual(action.get("type"), "ir.actions.act_window")
        self.assertEqual(action.get("res_model"), "audit.inspector")
