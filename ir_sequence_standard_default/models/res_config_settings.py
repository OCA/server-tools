# 2019  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    @api.multi
    def action_change_all_sequences(self):
        self.ensure_one()
        action = self.env.ref(
            'ir_sequence_standard_default.action_sequence_standard_default')
        return action.read()[0]
