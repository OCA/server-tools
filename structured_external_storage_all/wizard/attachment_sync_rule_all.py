# Copyright 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrAttachmentSyncRuleAll(models.TransientModel):
    """
    This wizard will Sync all the existing active rules
    """
    _name = "ir.attachment.sync.rule.all"
    _description = "Sync all the existing rules"

    @api.multi
    def run_sync_now_all(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for this in self.env['ir.attachment.sync.rule'].browse(active_ids):
            this.run_sync_now()
        return {'type': 'ir.actions.act_window_close'}
