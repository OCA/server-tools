# coding: utf-8
# @ 2016 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import base64
import os


class IrAttachmentMetadata(models.Model):
    _inherit = 'ir.attachment.metadata'

    task_id = fields.Many2one('external.file.task', string='Task')
    location_id = fields.Many2one(
        'external.file.location', string='Location',
        related='task_id.location_id', store=True)
    file_type = fields.Selection(
        selection_add=[
            ('export_external_location',
             'Export File (External location)')
        ])

    @api.multi
    def _run(self):
        super(IrAttachmentMetadata, self)._run()
        if self.file_type == 'export_external_location':
            protocols = self.env['external.file.location']._get_classes()
            location = self.location_id
            cls = protocols.get(location.protocol)[1]
            path = os.path.join(self.task_id.filepath, self.datas_fname)
            with cls.connect(location) as conn:
                datas = base64.decodestring(self.datas)
                conn.setcontents(path, data=datas)
