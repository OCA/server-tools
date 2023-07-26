# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

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
        attached = []
        for res_id in res.keys():
            mail = res[res_id]
            partner_ids = "partner_ids" in mail and mail["partner_ids"] or False
            if not partner_ids:
                continue
            for partner in self.env["res.partner"].browse(partner_ids):
                for lang_attach in self.ir_attachment_language_ids.filtered(
                    lambda a: a.lang == partner.lang
                ):
                    if lang_attach.attachment_id.id in attached:
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
