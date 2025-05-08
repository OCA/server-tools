# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    ir_attachment_language_method = fields.Selection(
        selection=[
            ("partner_lang", "Partner Language"),
            ("template_lang", "Template Language"),
        ],
        string="Language Attachment Method",
        default="partner_lang",
    )
    ir_attachment_language_ids = fields.One2many(
        string="Language Dependent Attachments",
        comodel_name="ir.attachment.language",
        inverse_name="mail_template_id",
    )

    def generate_email(self, res_ids, fields=None):
        self.ensure_one()
        multi = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi = False
        res = super().generate_email(res_ids, fields)
        lang_codes = dict(self._render_lang(res_ids))
        for res_id in res.keys():
            attached = []
            lang_code_list = []
            if self.ir_attachment_language_method == "partner_lang":
                mail = res[res_id]
                partner_ids = "partner_ids" in mail and mail["partner_ids"] or False
                partners = self.env["res.partner"].browse(partner_ids)
                lang_code_list = [p.lang for p in partners]
            elif self.ir_attachment_language_method == "template_lang":
                lang_code_list = [lang_codes.get(res_id)]
            for lang_code in lang_code_list:
                for lang_attach in self.ir_attachment_language_ids.filtered(
                    lambda a: a.lang == lang_code
                ):
                    if lang_attach.id in attached:
                        continue
                    if not res[res_id].get("attachments"):
                        res[res_id]["attachments"] = []
                    res[res_id]["attachments"].append(
                        (
                            lang_attach.attachment_id.name,
                            lang_attach.attachment_id.datas,
                        )
                    )
                    attached.append(lang_attach.id)
        return multi and res or res[res_ids[0]]
