# coding: utf-8
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#   @author: Joel Grand-Guillaume @ Camptocamp SA
# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import hashlib
from base64 import b64decode


class IrAttachmentMetadata(models.Model):
    _name = 'ir.attachment.metadata'
    _inherits = {'ir.attachment': 'attachment_id'}

    internal_hash = fields.Char(store=True, compute='_compute_hash')
    external_hash = fields.Char()
    attachment_id = fields.Many2one('ir.attachment', required=True,
                                    ondelete='cascade')

    @api.depends('datas', 'external_hash')
    def _compute_hash(self):
        if self.datas:
            self.internal_hash = hashlib.md5(b64decode(self.datas)).hexdigest()
        if self.external_hash and self.internal_hash != self.external_hash:
            raise UserError(_('File corrupted'),
                            _("Something was wrong with the retreived file, "
                              "please relaunch the task."))
