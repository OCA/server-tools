# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class IrAttachmentMetadata(models.Model):
    _inherit = 'ir.attachment.metadata'

    sync_date = fields.Datetime()
    state = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('done', 'Done'),
        ], readonly=False, required=True, default='pending')
    state_message = fields.Text()
    task_id = fields.Many2one('external.file.task', string='Task')
    location_id = fields.Many2one(
        'external.file.location', string='Location',
        related='task_id.location_id', store=True)
