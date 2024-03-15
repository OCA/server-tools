# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    @api.model
    def _get_tier_validation_model_names(self):
        res = super(TierDefinition, self)._get_tier_validation_model_names()
        res.append("request.request")
        return res
