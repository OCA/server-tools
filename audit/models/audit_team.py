# -*- coding: utf-8 -*-
"""Audit Team class for the Audit module."""

from odoo import fields, models


class AuditTeam(models.Model):
    """Audit Team class for the Audit module."""

    _name = "audit.team"
    _description = "Audit Team"

    _name_unique = models.Constraint("UNIQUE(name)", "Team name must be unique!")

    name = fields.Char(required=True)
    team_member_ids = fields.Many2many(
        comodel_name="audit.inspector",
        relation="audit_team_member_rel",
        column1="team_id",
        column2="user_id",
        string="Team Members",
    )
    # Leaders can see everyone's snapshots in that team
    team_leader_ids = fields.Many2many(
        comodel_name="audit.inspector",
        relation="audit_team_leader_rel",
        column1="team_id",
        column2="user_id",
        string="Team Leaders",
    )
