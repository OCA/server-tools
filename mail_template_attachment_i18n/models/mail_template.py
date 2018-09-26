# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    ir_attachment_language_ids = fields.One2many(
        string='Language Dependent Attachments',
        comodel_name='ir.attachment.language',
        inverse_name='mail_template_id',
    )

    @api.multi
    def generate_email(self, res_ids, fields=None):
        self.ensure_one()
        res = super(MailTemplate, self).generate_email(
            res_ids, fields
        )

        attached = []
        for res_id in res.keys():
            mail = res[res_id]
            partner_ids = mail['partner_ids']
            if not partner_ids:
                continue
            for partner_id in partner_ids:
                partner = self.env['res.partner'].browse(partner_id)
                for lang_attach in self.ir_attachment_language_ids.filtered(
                        lambda a: a.lang == partner.lang):
                    if lang_attach.attachment_id.id in attached:
                        continue
                    if 'attachments' not in res[res_id] or not \
                            res[res_id]['attachments']:
                        res[res_id]['attachments'] = []
                    res[res_id]['attachments'].append((
                        lang_attach.attachment_id.name,
                        lang_attach.attachment_id.datas))
                    attached.append(lang_attach.id)
        return res
