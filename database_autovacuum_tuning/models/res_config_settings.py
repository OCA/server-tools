# Copyright 2026 Camptocamp (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    autovacuum_vacuum_max_threshold = fields.Integer(
        config_parameter="database_autovacuum_tuning.autovacuum_vacuum_max_threshold",
    )
    autovacuum_vacuum_analyze_max_threshold = fields.Integer(
        config_parameter="database_autovacuum_tuning.autovacuum_vacuum_analyze_max_threshold",
    )
