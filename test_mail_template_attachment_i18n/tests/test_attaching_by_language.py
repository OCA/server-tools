# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestAttachingByLanguage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.english_partner = cls.env["res.partner"].create(
            {"name": "English Partner", "email": "test@english.nl", "lang": "en_US"}
        )
        cls.dutch_partner = cls.env["res.partner"].create(
            {"name": "Dutch Partner", "email": "test@dutch.nl", "lang": False}
        )
        cls.attachment = cls.env["ir.attachment"].create(
            {"name": "File", "type": "binary"}
        )
        cls.template = cls.env["mail.template"].create(
            {
                "name": "Test",
                "model_id": cls.env["ir.model"]
                .search([("model", "=", "sale.order")])
                .id,
                "ir_attachment_language_ids": [
                    (0, False, {"attachment_id": cls.attachment.id, "lang": "en_US"})
                ],
                "attachment_ids": [(0, False, {"name": "File 2", "type": "binary"})],
                "lang": "{{ object.partner_id.lang }}",
                "partner_to": "{{ object.partner_id.id }}",
                "body_html": "Test",
            }
        )

    def test_attaching(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.english_partner.id,
            }
        )
        composer_form = Form(
            self.env["mail.compose.message"].with_context(
                **{
                    "default_composition_mode": "comment",
                    "default_model": sale_order._name,
                    "default_res_id": sale_order.id,
                }
            )
        )
        composer_form.body = "<p>Test Body</p>"
        composer_form.partner_ids.add(sale_order.partner_id)
        composer_form.template_id = self.template
        composer = composer_form.save()
        self.assertEqual(len(composer.attachment_ids), 2)

    def test_not_attaching(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.dutch_partner.id,
            }
        )
        composer_form = Form(
            self.env["mail.compose.message"].with_context(
                **{
                    "default_composition_mode": "comment",
                    "default_model": sale_order._name,
                    "default_res_id": sale_order.id,
                }
            )
        )
        composer_form.body = "<p>Test Body</p>"
        composer_form.partner_ids.add(sale_order.partner_id)
        composer_form.template_id = self.template
        composer = composer_form.save()
        self.assertEqual(len(composer.attachment_ids), 1)
