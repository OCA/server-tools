# Copyright 2024 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.tests import tagged

from odoo.addons.mail.tests.common import MailCommon


@tagged("mail_template", "-at_install", "post_install")
class TestMailTemplateAttachmentPerLang(MailCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("fr_FR")
        cls.partner_fr = cls.env["res.partner"].create(
            {
                "name": "French Partner",
                "email": "french@example.com",
                "lang": "fr_FR",
            }
        )
        cls.partner_en = cls.env["res.partner"].create(
            {
                "name": "English Partner",
                "email": "english@example.com",
                "lang": "en_US",
            }
        )

        cls.attachment_fr = cls.env["ir.attachment"].create(
            {
                "name": "terms_fr.pdf",
                "type": "binary",
                "datas": base64.b64encode(b"French terms content"),
            }
        )
        cls.attachment_en = cls.env["ir.attachment"].create(
            {
                "name": "terms_en.pdf",
                "type": "binary",
                "datas": base64.b64encode(b"English terms content"),
            }
        )

        cls.mail_template = cls.env["mail.template"].create(
            {
                "name": "Test i18n Template",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "subject": "Test subject",
                "body_html": "<p>Test body</p>",
                "partner_to": "{{ object.id }}",
                "lang": "{{ object.lang }}",
                "ir_attachment_language_method": "template_lang",
                "ir_attachment_language_ids": [
                    (
                        0,
                        0,
                        {
                            "lang": "fr_FR",
                            "attachment_id": cls.attachment_fr.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "lang": "en_US",
                            "attachment_id": cls.attachment_en.id,
                        },
                    ),
                ],
            }
        )

    def test_template_lang_method_french(self):
        # Sending to a French partner should attach the French file
        render_results = self.mail_template._generate_template(
            [self.partner_fr.id],
            [
                "attachment_ids",
                "body_html",
                "email_from",
                "partner_to",
                "report_template_ids",
                "subject",
            ],
        )
        attachments = render_results[self.partner_fr.id].get("attachment_ids", [])
        attachment_records = self.env["ir.attachment"].browse(attachments)
        attachment_names = attachment_records.mapped("name")
        self.assertIn("terms_fr.pdf", attachment_names)
        self.assertNotIn("terms_en.pdf", attachment_names)

    def test_template_lang_method_english(self):
        # Sending to an English partner should attach the English file
        render_results = self.mail_template._generate_template(
            [self.partner_en.id],
            [
                "attachment_ids",
                "body_html",
                "email_from",
                "partner_to",
                "report_template_ids",
                "subject",
            ],
        )
        attachments = render_results[self.partner_en.id].get("attachment_ids", [])
        attachment_records = self.env["ir.attachment"].browse(attachments)
        attachment_names = attachment_records.mapped("name")
        self.assertIn("terms_en.pdf", attachment_names)
        self.assertNotIn("terms_fr.pdf", attachment_names)

    def test_partner_lang_method(self):
        # With partner_lang method, attachments match partner language
        self.mail_template.ir_attachment_language_method = "partner_lang"
        render_results = self.mail_template._generate_template(
            [self.partner_fr.id],
            [
                "attachment_ids",
                "body_html",
                "email_from",
                "partner_to",
                "report_template_ids",
                "subject",
            ],
        )
        attachments = render_results[self.partner_fr.id].get("attachment_ids", [])
        attachment_records = self.env["ir.attachment"].browse(attachments)
        attachment_names = attachment_records.mapped("name")
        self.assertIn("terms_fr.pdf", attachment_names)
        self.assertNotIn("terms_en.pdf", attachment_names)

    def test_no_method_set(self):
        # With no method set, no language-specific attachments are added
        self.mail_template.ir_attachment_language_method = False
        render_results = self.mail_template._generate_template(
            [self.partner_fr.id],
            [
                "attachment_ids",
                "body_html",
                "email_from",
                "partner_to",
                "report_template_ids",
                "subject",
            ],
        )
        attachments = render_results[self.partner_fr.id].get("attachment_ids", [])
        self.assertFalse(attachments)

    def test_batch_multiple_partners(self):
        # Batch rendering attaches correct files per language
        render_results = self.mail_template._generate_template(
            [self.partner_fr.id, self.partner_en.id],
            [
                "attachment_ids",
                "body_html",
                "email_from",
                "partner_to",
                "report_template_ids",
                "subject",
            ],
        )
        fr_attachments = render_results[self.partner_fr.id].get("attachment_ids", [])
        fr_attachment_records = self.env["ir.attachment"].browse(fr_attachments)
        fr_names = fr_attachment_records.mapped("name")
        en_attachments = render_results[self.partner_en.id].get("attachment_ids", [])
        en_attachment_records = self.env["ir.attachment"].browse(en_attachments)
        en_names = en_attachment_records.mapped("name")
        self.assertIn("terms_fr.pdf", fr_names)
        self.assertNotIn("terms_en.pdf", fr_names)
        self.assertIn("terms_en.pdf", en_names)
        self.assertNotIn("terms_fr.pdf", en_names)

    def test_send_mail_with_lang_attachments(self):
        # Full send_mail flow includes language-specific attachments
        with self.mock_mail_gateway():
            mail = self.mail_template.send_mail(self.partner_fr.id)
        mail_record = self.env["mail.mail"].browse(mail)
        attachment_names = mail_record.attachment_ids.mapped("name")
        self.assertIn("terms_fr.pdf", attachment_names)
        self.assertNotIn("terms_en.pdf", attachment_names)

    def test_partner_lang_with_fixed_template_lang(self):
        # Test that even if the template body is forced to English,
        # the attachments follow the recipient's language.
        self.mail_template.write(
            {
                "lang": "en_US",
                "partner_to": str(self.partner_en.id),
                "ir_attachment_language_method": "partner_lang",
            }
        )
        # English recipient --> Should get English attachment
        render_results = self.mail_template._generate_template(
            [self.partner_en.id],
            ["attachment_ids"],
        )
        result = render_results[self.partner_en.id]
        attachments = self.env["ir.attachment"].browse(result.get("attachment_ids", []))
        attachment_names = attachments.mapped("name")
        self.assertIn("terms_en.pdf", attachment_names)
        self.assertNotIn("terms_fr.pdf", attachment_names)
        # Change recipient to French partner
        # The body remains English (lang='en_US'), but attachments must switch to French
        self.mail_template.write(
            {
                "partner_to": str(self.partner_fr.id),
            }
        )
        render_results = self.mail_template._generate_template(
            [self.partner_fr.id],
            ["attachment_ids"],
        )
        result = render_results[self.partner_fr.id]
        attachments = self.env["ir.attachment"].browse(result.get("attachment_ids", []))
        attachment_names = attachments.mapped("name")
        # Verify that the logic correctly prioritized the recipient's language
        self.assertIn("terms_fr.pdf", attachment_names)
        self.assertNotIn("terms_en.pdf", attachment_names)
