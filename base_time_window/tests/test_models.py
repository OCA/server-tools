from odoo import fields, models


class TestTimeWindowModel(models.Model):
    _name = "test.time.window.model"
    _description = "Test Time Window Model"
    _inherit = "time.window.mixin"
    _time_window_overlap_check_field = "partner_id"

    partner_id = fields.Many2one(
        "res.partner", required=True, index=True, ondelete="cascade"
    )
