# Copyright 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AttachmentSyncCreateMetasAll(models.TransientModel):
    """
    This wizard will Create the metadata for the selected Sync rules
    """
    _name = "attachment.sync.create.metas.all"
    _description = "Create the metadatas to be queued for the sync"

    @api.multi
    def queue_for_sync_all(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for this in self.env['ir.attachment.sync.rule'].browse(active_ids):
            this.queue_for_sync()
        return {'type': 'ir.actions.act_window_close'}
