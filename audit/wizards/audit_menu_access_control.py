"""Classes and backend functionality for Audit module menu access control."""

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class AuditMenuAccessControl(models.TransientModel):
    """
    Class and functionality to control what users can see when opening Audit menu items.
    """

    _name = "audit.menu.access.control"
    _description = "Simple Audit Menu Access Control"

    @api.model
    def check_user_access(self, user_id=None):
        """
        Simple function to check if current user should have access.
        """
        logged_in_user = self.env.user
        admin_user = logged_in_user.has_group("base.group_system")
        # Admin users should be able to see and click menu items
        if admin_user:
            return logged_in_user, True

        user = self.env["res.users"].search([("id", "=", user_id)])
        if user:
            return user, True
        return None, False

    @api.model
    def _get_user_inspector(self, user):
        """
        Get the inspector record associated with a user.
        """
        return self.env["audit.inspector"].search(
            [("res_user_id", "=", user.id)], limit=1
        )

    @api.model
    def _get_team_member_ids(self, user_inspector):
        """
        Get all team member IDs from teams where user is a leader.
        """
        _teams = self.env["audit.team"].search(
            [("team_leader_ids", "in", [user_inspector.id])]
        )
        if not _teams:
            return []

        all_team_member_ids = []
        for team in _teams:
            # Add team members
            all_team_member_ids.extend(team.team_member_ids.ids)
            # Add team leaders (including themselves)
            all_team_member_ids.extend(team.team_leader_ids.ids)

        # Remove duplicates and ensure user inspector is included
        all_team_member_ids = list(set(all_team_member_ids))
        if user_inspector.id not in all_team_member_ids:
            all_team_member_ids.append(user_inspector.id)

        return all_team_member_ids

    @api.model
    def _get_inspector_based_domain(self, user, domain_field="inspector_id"):
        """
        Get domain for inspector-based access control.
        domain_field can be: "id", "inspector_id", "snapshot_id.inspector_id"
        """
        admin_user = user.has_group("base.group_system")

        if admin_user:
            return []

        user_inspector = self._get_user_inspector(user)
        if not user_inspector:
            return [("id", "=", False)]

        team_member_ids = self._get_team_member_ids(user_inspector)
        if team_member_ids:
            # User is team leader - show records from all team members and leaders
            return [(domain_field, "in", team_member_ids)]

        # User is not team leader - show only their own records
        return [(domain_field, "=", user_inspector.id)]

    @api.model
    def _get_team_leadership_domain(self, user):
        """
        Get domain for team leadership access control.
        """
        admin_user = user.has_group("base.group_system")

        if admin_user:
            return []

        user_inspector = self._get_user_inspector(user)
        if not user_inspector:
            return [("id", "=", False)]

        # Check if inspector is a team leader of any teams
        team_lead = self.env["audit.team"].search(
            [("team_leader_ids", "in", [user_inspector.id])]
        )
        if team_lead:
            # User is team leader - show only teams they lead
            return [("team_leader_ids", "in", [user_inspector.id])]

        # User is not a team leader - show no teams
        return [("id", "=", False)]

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    @api.model
    def _build_standard_action(
        self,
        user_id,
        name,
        res_model,
        domain_type="inspector",
        domain_field="inspector_id",
        context=None,
    ):
        """
        Build a standard menu action with access control.

        Why not build these actions in XML?  Because building them in Python
        allows for greater control and customization, logging and tracking of who
        is trying to enter which menus and when.
        """
        user, allow_access = self.check_user_access(user_id=user_id)
        if allow_access:
            if domain_type == "team":
                domain = self._get_team_leadership_domain(user)
            else:
                domain = self._get_inspector_based_domain(user, domain_field)

            action = {
                "name": name,
                "type": "ir.actions.act_window",
                "res_model": res_model,
                "view_mode": "list,form",
                "target": "current",
                "domain": domain,
            }

            if context:
                action["context"] = context

            return action

        # Show access denied message if not allow_access
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": self.env._("You may not access this menu item."),
                "type": "warning",
                "sticky": False,
            },
        }

    @api.model
    def inspectors_menu_action(self, user_id=None):
        """
        Action method that checks access and returns appropriate action
        """
        return self._build_standard_action(
            user_id=user_id,
            name="Inspectors",
            res_model="audit.inspector",
            domain_type="inspector",
            domain_field="id",
        )

    @api.model
    def teams_menu_action(self, user_id=None):
        """
        Return the Audit Teams action
        """
        return self._build_standard_action(
            user_id=user_id,
            name="Audit Teams",
            res_model="audit.team",
            domain_type="team",
        )

    @api.model
    def snapshots_menu_action(self, user_id=None):
        """
        Return the Snapshots Menu Action.
        """
        return self._build_standard_action(
            user_id=user_id,
            name="Snapshots",
            res_model="audit.snapshot",
            domain_type="inspector",
            domain_field="inspector_id",
        )

    @api.model
    def archived_snapshots_menu_action(self, user_id=None):
        """
        Return the Archived Snapshots action.
        """
        return self._build_standard_action(
            user_id=user_id,
            name="Archived Snapshots",
            res_model="audit.snapshot",
            domain_type="inspector",
            domain_field="inspector_id",
            context={"search_default_archived_snapshots": 1},
        )

    @api.model
    def snapshot_sections_menu_action(self, user_id=None):
        """
        Return the Snapshot Sections action.
        """
        return self._build_standard_action(
            user_id=user_id,
            name="Snapshot Sections",
            res_model="audit.snapshot_section",
            domain_type="inspector",
            domain_field="snapshot_id.inspector_id",
        )

    @api.model
    def snapshot_questions_menu_action(self, user_id=None):
        """
        Return the Snapshot Questions action.
        """
        return self._build_standard_action(
            user_id=user_id,
            name="Snapshot Questions",
            res_model="audit.snapshot_question",
            domain_type="inspector",
            domain_field="snapshot_id.inspector_id",
        )
