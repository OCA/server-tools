# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Activate me back when modules are migrated

    module_base_tier_validation_formula = fields.Boolean(string="Tier Formula")
    # module_base_tier_validation_forward = fields.Boolean("Tier Forward & Backward")
    # module_base_tier_validation_server_action = fields.Boolean("Tier Server Action")
    # module_base_tier_validation_report = fields.Boolean("Tier Reports")
