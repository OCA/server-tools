# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAttachingByLanguage(TransactionCase):
    def setUp(self):
        super().setUp()
        self.english_partner = self.env['res.partner'].create({
            'name': 'English Partner',
            'email': 'test@english.nl',
            'lang': 'en_US'
        })
        self.dutch_partner = self.env['res.partner'].create({
            'name': 'Dutch Partner',
            'email': 'test@dutch.nl',
            'lang': False
        })
        self.attachment = self.env['ir.attachment'].create({
            'name': 'File',
            'type': 'binary'
        })
        self.template = self.env['mail.template'].create({
            'name': 'Test',
            'model_id': self.env['ir.model'].search(
                [('model', '=', 'sale.order')]).id,
            'ir_attachment_language_ids': [(0, False, {
                'attachment_id': self.attachment.id,
                'lang': 'en_US'
            })],
            'attachment_ids': [(0, False, {
                'name': 'File 2',
                'type': 'binary'
            })],
            'lang': '${object.partner_id.lang}',
            'email_to': '${object.partner_id.email}',
            'body_html': 'Test'
        })

    def test_attaching(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.english_partner.id,
        })
        res = self.env['mail.compose.message'].create({
            'model': 'sale.order',
            'res_id': sale_order.id,
            'email_to': ['test@english.nl'],
            'use_template': True,
            'template_id': self.template.id
        })
        res.onchange_template_id_wrapper()
        self.assertEqual(len(res.attachment_ids), 2)

    def test_not_attaching(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.dutch_partner.id,
        })
        res = self.env['mail.compose.message'].create({
            'model': 'sale.order',
            'res_id': sale_order.id,
            'email_to': ['test@dutch.nl'],
            'use_template': True,
            'template_id': self.template.id
        })
        res.onchange_template_id_wrapper()
        self.assertEqual(len(res.attachment_ids), 1)
