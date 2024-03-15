# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class TierDefinition(models.AbstractModel):
    _inherit = "tier.definition"

    summary_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        domain="[('model_id', '=', model_id),('store', '=', True)]",
        help="If defined, the value of that field will be used in the summary of the review.",
    )
