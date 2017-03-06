# coding: utf-8
# @ 2015 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from base64 import b64decode
import hashlib
import logging
import odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class IrAttachmentMetadata(models.Model):
    _name = 'ir.attachment.metadata'
    _inherits = {'ir.attachment': 'attachment_id'}
    _inherit = ['mail.thread']

    internal_hash = fields.Char(
        store=True, compute='_compute_hash',
        help="File hash computed with file data to be compared "
             "to external hash when provided.")
    external_hash = fields.Char(
        help="File hash comes from the external owner of the file.\n"
             "If provided allow to check than downloaded file "
             "is the exact copy of the original file.")
    attachment_id = fields.Many2one(
        'ir.attachment', required=True, ondelete='cascade',
        help="Link to ir.attachment model ")
    file_type = fields.Selection(
        selection=[],
        string="File type",
        help="The file type determines an import method to be used "
        "to parse and transform data before their import in ERP or an export")
    sync_date = fields.Datetime()
    state = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('done', 'Done'),
        ], readonly=False, required=True, default='pending')
    state_message = fields.Text()

    @api.depends('datas', 'external_hash')
    def _compute_hash(self):
        for attachment in self:
            if attachment.datas:
                attachment.internal_hash = hashlib.md5(
                    b64decode(attachment.datas)).hexdigest()
            if attachment.external_hash and\
               attachment.internal_hash != attachment.external_hash:
                raise UserError(
                    _("File corrupted: Something was wrong with "
                      "the retrieved file, please relaunch the task."))

    @api.model
    def run_attachment_metadata_scheduler(self, domain=None):
        if domain is None:
            domain = [('state', '=', 'pending')]
        attachments = self.search(domain)
        if attachments:
            return attachments.run()
        return True

    @api.multi
    def run(self):
        """
        Run the process for each attachment metadata
        """
        for attachment in self:
            with api.Environment.manage():
                with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(
                        new_cr, self.env.uid, self.env.context)
                    attach = attachment.with_env(new_env)
                    try:
                        attach._run()
                    except Exception, e:
                        attach.env.cr.rollback()
                        _logger.exception(e)
                        attach.write(
                            {
                                'state': 'failed',
                                'state_message': e,
                            })
                        attach.env.cr.commit()
                    else:
                        vals = {
                            'state': 'done',
                            'sync_date': fields.Datetime.now(),
                        }
                        attach.write(vals)
                        attach.env.cr.commit()
        return True

    @api.multi
    def _run(self):
        self.ensure_one()
        _logger.info('Start to process attachment metadata id %s' % self.id)

    @api.multi
    def set_done(self):
        """
        Manually set to done
        """
        message = "Manually set to done by %s" % self.env.user.name
        self.write({'state_message': message, 'state': 'done'})
