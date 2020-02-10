# @ 2016 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import os


class IrAttachmentMetadata(models.Model):
    _inherit = 'ir.attachment.metadata'

    task_id = fields.Many2one('storage.backend.task', string='Task')
    storage_backend_id = fields.Many2one(
        'storage.backend', string='Storage Backend',
        related='task_id.backend_id', store=True)
    file_type = fields.Selection(
        selection_add=[
            ('export',
             'Export File (External location)')
        ])

    def _run(self):
        super()._run()
        if self.file_type == 'export':
            path = os.path.join(self.task_id.filepath, self.datas_fname)
            self.storage_backend_id._add_b64_data(path, self.datas)

    def _get_failure_emails(self):
        res = super()._get_failure_emails()
        if self.task_id.emails:
            res = self.task_id.emails
        return res
