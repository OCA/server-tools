# Copyright 2023-2024 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class ChangesetFieldRule(models.Model):
    _inherit = "changeset.field.rule"

    create_tier_review = fields.Boolean(
        string="Create tier review?",
        default=False,
    )
    field_name = fields.Char(compute="_compute_field_name")
    field_model_id = fields.Many2one(
        compute="_compute_field_model_id",
        comodel_name="ir.model",
    )
    tier_parent_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        domain="""
        [('model_id', '=', field_model_id),
        ('ttype', '=', 'many2one'),
        ('readonly', '=', False)]
        """,
        string="Tier parent field",
    )
    tier_model = fields.Char(compute="_compute_tier_model")
    tier_definition_id = fields.Many2one(
        comodel_name="tier.definition",
        domain="[('model', '=', tier_model)]",
        string="Tier definition",
    )
    allowed_summary_model = fields.Char(
        compute="_compute_allowed_summary_model", compute_sudo=True
    )
    summary_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        domain="[('model_id.model', '=', allowed_summary_model),('store', '=', True)]",
        help="If defined, the value of that field will be used in the summary of the review.",
    )

    @api.depends("field_id")
    def _compute_field_name(self):
        for item in self:
            item.field_name = item.field_id.name

    @api.depends("field_id")
    def _compute_field_model_id(self):
        for item in self:
            if item.field_id:
                item.field_model_id = item.field_id.model_id
            else:
                item.field_model_id = item.field_model_id

    @api.depends("create_tier_review", "tier_parent_field_id", "model_id")
    def _compute_tier_model(self):
        for item in self:
            if item.create_tier_review:
                item.tier_model = (
                    item.tier_parent_field_id.relation or item.model_id.model
                )
            else:
                item.tier_model = item.tier_model

    @api.depends("field_id", "field_ttype", "field_relation", "model_id")
    def _compute_allowed_summary_model(self):
        for item in self:
            if item.field_ttype == "one2many":
                item.allowed_summary_model = item.field_relation
            else:
                item.allowed_summary_model = item.model_id.model
