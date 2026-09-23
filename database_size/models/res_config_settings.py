# Copyright 2025 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    database_size_purge = fields.Boolean(
        string="Purge Older Model Size Measurements",
        config_parameter="database_size.purge_enable",
    )
    database_size_retention_daily = fields.Integer(
        string="Keep Daily Measurements for",
        config_parameter="database_size.retention_daily",
        help=(
            "The period of time (in days) during which the daily database size "
            "measurements are kept. If set to 0, measurements will be kept "
            "forever."
        ),
        default="366",
    )
    database_size_retention_monthly = fields.Integer(
        string="Keep Monthly Measurements for",
        config_parameter="database_size.retention_monthly",
        help=(
            "The period of time (in days) during which database size measurmeents "
            "are kept of the first day of each month. If set to 0, measurements "
            "will be kept forever."
        ),
        default="0",
    )
