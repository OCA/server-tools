# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class TierReview(models.Model):
    _name = "tier.review"

    status = fields.Selection(
        selection=[("pending", "Pending"),
                   ("rejected", "Rejected"),
                   ("approved", "Approved")],
        default="pending",
    )
    model = fields.Char(string='Related Document Model', index=True)
    res_id = fields.Integer(string='Related Document ID', index=True)
    definition_id = fields.Many2one(
        comodel_name="tier.definition",
    )
    review_type = fields.Selection(
        related="definition_id.review_type", readonly=True,
    )
    reviewer_id = fields.Many2one(
        related="definition_id.reviewer_id", readonly=True,
    )
    reviewer_group_id = fields.Many2one(
        related="definition_id.reviewer_group_id", readonly=True,
    )
    reviewer_ids = fields.Many2many(
        string="Reviewers", comodel_name="res.users",
        compute="_compute_reviewer_ids", store=True,
    )
    sequence = fields.Integer(string="Tier")

    @api.multi
    @api.depends('reviewer_id', 'reviewer_group_id', 'reviewer_group_id.users')
    def _compute_reviewer_ids(self):
        for rec in self:
            rec.reviewer_ids = rec.reviewer_id + rec.reviewer_group_id.users
