# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class TierDefinition(models.Model):
    _name = "tier.definition"
    _rec_name = "model_id"

    @api.model
    def _get_tier_validation_model_names(self):
        res = []
        return res

    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Referenced Model",
    )
    model = fields.Char(
        related='model_id.model', index=True, store=True,
    )
    review_type = fields.Selection(
        string="Validated by", default="individual",
        selection=[("individual", "Specific user"),
                   ("group", "Any user in a specific group.")]
    )
    reviewer_id = fields.Many2one(
        comodel_name="res.users", string="Reviewer",
    )
    reviewer_group_id = fields.Many2one(
        comodel_name="res.groups", string="Reviewer group",
    )
    python_code = fields.Text(
        string='Tier Definition Expression',
        help="Write Python code that defines when this tier confirmation "
             "will be needed. The result of executing the expresion must be "
             "a boolean.",
        default="""# Available locals:\n#  - rec: current record""",
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=30)
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company",
        default=lambda self: self.env["res.company"]._company_default_get(
            "tier.definition"),
    )

    @api.onchange('model_id')
    def onchange_model_id(self):
        return {'domain': {
            'model_id': [
                ('model', 'in', self._get_tier_validation_model_names())]}}
