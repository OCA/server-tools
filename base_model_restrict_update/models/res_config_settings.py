# Copyright 2024 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    excluded_models_from_readonly = fields.Char(
        "Excluded Models from Read-only",
        help="Specified models, separated by commas, will be exempt from the read-only "
        "restriction for read-only users.",
        config_parameter="base_model_restrict_update.excluded_models_from_readonly",
    )
