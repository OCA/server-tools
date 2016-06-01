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
        selection="_get_file_type",
        string="File type",
        help="The file type determines an import method to be used "
        "to parse and transform data before their import in ERP")

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

    def _get_file_type(self):
        """This is the method to be inherited for adding file types
        The basic import do not apply any parsing or transform of the file.
        The file is just added as an attachement
        """
        return [('basic_import', 'Basic import')]
