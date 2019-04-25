# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrAttachmentLanguage(models.Model):
    _name = 'ir.attachment.language'

    mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Template',
        required=True,
        ondelete='cascade',
    )

    lang = fields.Selection(
        selection=lambda self: self.env['res.lang'].get_installed(),
        string='Language',
        required=True,
    )

    attachment_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='Attachment',
        required=True,
        ondelete='cascade',
    )
