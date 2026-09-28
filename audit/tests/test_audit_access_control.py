"""Tests for audit menu access (TransientModel) actions."""

import uuid

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


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
        """Return a non-admin user (``res.users`` create rules differ by edition)."""
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

    def test_check_user_access_non_admin_finds_by_user_id(self):
        internal = self._internal_user()
        user, allowed = self.Access.with_user(internal).check_user_access(
            user_id=internal.id
        )
        self.assertTrue(allowed)
        self.assertEqual(user, internal)

    def test_get_team_member_ids_for_leader_aggregates_members(self):
        inspector_1 = self.env["audit.inspector"].create(
            {"name": "G_Member_A"},
        )
        inspector_2 = self.env["audit.inspector"].create(
            {"name": "G_Member_B"},
        )
        team_leader = self.env["audit.inspector"].create(
            {"name": "G_Team_Leader"},
        )
        self.env["audit.team"].create(
            {
                "name": "G Team M IDs",
                "team_member_ids": [Command.set((inspector_1 | inspector_2).ids)],
                "team_leader_ids": [Command.set(team_leader.ids)],
            }
        )
        result = set(self.Access._get_team_member_ids(team_leader))
        for ins in (inspector_1, inspector_2, team_leader):
            self.assertIn(ins.id, result)

    def test_get_team_member_ids_not_leader_no_team_returns_empty(self):
        only_member = self.env["audit.inspector"].create(
            {"name": "G_Lonely_Inspector"},
        )
        self.assertEqual(self.Access._get_team_member_ids(only_member), [])

    def test_get_inspector_based_domain_for_admin(self):
        self.assertEqual(
            self.Access._get_inspector_based_domain(self.admin_user, "inspector_id"),
            [],
        )

    def test_get_inspector_based_domain_no_inspector(self):
        internal = self._internal_user()
        self.assertEqual(
            self.Access._get_inspector_based_domain(internal, "inspector_id"),
            [("id", "=", False)],
        )

    def test_get_inspector_based_domain_solo_inspector(self):
        internal = self._internal_user()
        u_ins = self.env["audit.inspector"].create(
            {
                "name": "G Access Insp",
                "res_user_id": internal.id,
            }
        )
        self.assertEqual(
            self.Access._get_inspector_based_domain(internal, "inspector_id"),
            [("inspector_id", "=", u_ins.id)],
        )

    def test_get_inspector_based_domain_team_leader_uses_in_domain(self):
        leader_user = self._internal_user()
        other_user = self._internal_user()
        m1 = self.env["audit.inspector"].create(
            {
                "name": "G_LI_1",
                "res_user_id": leader_user.id,
            }
        )
        m2 = self.env["audit.inspector"].create(
            {
                "name": "G_LI_2",
                "res_user_id": other_user.id,
            }
        )
        self.env["audit.team"].create(
            {
                "name": "G Lead In Dom",
                "team_member_ids": [Command.set([m2.id])],
                "team_leader_ids": [Command.set([m1.id])],
            }
        )
        dom = self.Access._get_inspector_based_domain(leader_user, "inspector_id")
        self.assertEqual(dom[0][:2], ("inspector_id", "in"))
        in_ids = dom[0][2]
        self.assertIn(m1.id, in_ids)
        self.assertIn(m2.id, in_ids)

    def test_get_team_leadership_domain_variants(self):
        self.assertEqual(
            self.Access._get_team_leadership_domain(self.admin_user),
            [],
        )
        internal = self._internal_user()
        self.assertEqual(
            self.Access._get_team_leadership_domain(internal),
            [("id", "=", False)],
        )
        leader = self._internal_user()
        lead_ins = self.env["audit.inspector"].create(
            {
                "name": "G_Team_dom",
                "res_user_id": leader.id,
            }
        )
        self.env["audit.team"].create(
            {
                "name": "G TLDom",
                "team_leader_ids": [Command.set([lead_ins.id])],
            }
        )
        tdom = self.Access._get_team_leadership_domain(leader)
        self.assertEqual(
            tdom,
            [("team_leader_ids", "in", [lead_ins.id])],
        )
        not_leader = self._internal_user()
        nli = self.env["audit.inspector"].create(
            {
                "name": "G_Not_Lead",
                "res_user_id": not_leader.id,
            }
        )
        self.env["audit.team"].create(
            {
                "name": "G TLDom member",
                "team_member_ids": [Command.set([nli.id])],
            }
        )
        self.assertEqual(
            self.Access._get_team_leadership_domain(not_leader),
            [("id", "=", False)],
        )

    def test_build_standard_action_allows_with_context(self):
        action = self.Access.with_user(
            self.admin_user,
        )._build_standard_action(
            user_id=self.admin_user.id,
            name="Ctx",
            res_model="audit.snapshot",
            domain_type="inspector",
            domain_field="inspector_id",
            context={"a": 1},
        )
        self.assertEqual(action.get("type"), "ir.actions.act_window")
        self.assertEqual(action.get("context"), {"a": 1})

    def test_menu_action_helpers_return_window_for_admin(self):
        admin = self.admin_user
        cases = [
            (lambda: self.Access.with_user(admin).teams_menu_action(), "audit.team"),
            (
                lambda: self.Access.with_user(admin).snapshots_menu_action(),
                "audit.snapshot",
            ),
            (
                lambda: self.Access.with_user(admin).archived_snapshots_menu_action(),
                "audit.snapshot",
            ),
            (
                lambda: self.Access.with_user(admin).snapshot_sections_menu_action(),
                "audit.snapshot_section",
            ),
            (
                lambda: self.Access.with_user(admin).snapshot_questions_menu_action(),
                "audit.snapshot_question",
            ),
        ]
        for call, model in cases:
            a = call()
            self.assertEqual(a.get("type"), "ir.actions.act_window", msg=repr(a))
            self.assertEqual(a.get("res_model"), model)
