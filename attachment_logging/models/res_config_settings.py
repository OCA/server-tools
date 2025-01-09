from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_attachment_log = fields.Boolean(
        config_parameter="attachment_logging.use_attachment_log",
        help="Log attachment operations in chatter",
    )
