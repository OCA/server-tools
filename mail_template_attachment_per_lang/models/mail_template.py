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

    def _generate_template_attachments(
        self, res_ids, render_fields, render_results=None
    ):
        self.ensure_one()
        res = super()._generate_template_attachments(
            res_ids, render_fields, render_results=render_results
        )
        recipient_values = {}  # Get recipients (to work with partner_lang)
        if self.ir_attachment_language_method == "partner_lang":
            recipient_fields = {"email_cc", "email_to", "partner_to"}
            self._generate_template_recipients(
                res_ids,
                recipient_fields,
                render_results=recipient_values,
            )
        lang_codes = dict(self._render_lang(res_ids))
        for res_id in res_ids:
            values = res.setdefault(res_id, {})
            attached = []
            lang_code_list = []
            if self.env.context.get("template_preview_lang"):
                lang = self.env.context.get("template_preview_lang")
                lang_codes = {res_id: lang for res_id in res_ids}
                lang_code_list = [lang_codes.get(res_id)]
            elif self.ir_attachment_language_method == "partner_lang":
                partner_ids = recipient_values.get(res_id, {}).get("partner_ids", [])
                partners = self.env["res.partner"].browse(partner_ids)
                lang_code_list = [p.lang for p in partners]
            elif self.ir_attachment_language_method == "template_lang":
                lang_code_list = [lang_codes.get(res_id)]
            for lang_code in lang_code_list:
                for lang_attach in self.ir_attachment_language_ids.filtered(
                    lambda a, lc=lang_code: a.lang == lc
                ):
                    if lang_attach.id in attached:
                        continue
                    if "attachment_ids" not in values:
                        values["attachment_ids"] = []
                    values["attachment_ids"].append(lang_attach.attachment_id.id)
                    attached.append(lang_attach.id)
        return res
