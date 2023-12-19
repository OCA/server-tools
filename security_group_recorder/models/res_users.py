#!/usr/bin/env python
from odoo import api, fields, models


class Users(models.Model):
    _inherit = "res.users"

    profiled_sessions_ids = fields.One2many(
        comodel_name="res.users.profiler.sessions",
        inverse_name="user_id",
        string="Profiled Sessions",
    )
    active_session_id = fields.Many2one(
        comodel_name="res.users.profiler.sessions",
        string="Profiled Session",
        compute="_compute_active_session_id",
        readonly=True,
    )
    is_profiled = fields.Boolean(
        string="Profiled",
        compute="_compute_active_session_id",
        default=False,
        readonly=True,
        help="Whether this user is being profiled or not.",
    )

    @api.depends("profiled_sessions_ids")
    def _compute_active_session_id(self):
        for rec in self:
            rec.active_session_id = rec.profiled_sessions_ids.filtered(
                lambda s: s.id and s.active
            )
            rec.is_profiled = bool(rec.active_session_id)
