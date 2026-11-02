# Copyright 2026 Syed Sameed Zafar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    phone_autoformat_format = fields.Selection(
        selection=[
            ("INTERNATIONAL", "International (+92 300 1234567)"),
            ("E164", "E.164 (+923001234567)"),
            ("NATIONAL", "National (0300 1234567)"),
            ("RFC3966", "RFC 3966 (tel:+92-300-1234567)"),
            ("off", "Disabled (do not format)"),
        ],
        string="Phone Number Format",
        config_parameter="phone_autoformat.format",
        default="INTERNATIONAL",
        help="Format applied to phone numbers when a record is edited or saved.",
    )
    phone_autoformat_multiple = fields.Selection(
        selection=[
            ("multiple", "Allow several numbers in one field"),
            ("single", "One number per field"),
        ],
        string="Numbers per Field",
        config_parameter="phone_autoformat.multiple",
        default="multiple",
        help="With 'several numbers', separate them with a comma, semicolon "
        "or new line; each one is formatted on its own.",
    )
