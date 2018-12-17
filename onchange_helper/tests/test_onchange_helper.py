# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestOnchangeHelper(TransactionCase):
    def test01_partner_parent(self):
        main_partner = self.env.ref('base.main_partner')
        input_vals = dict(partner_id=main_partner.id)
        updated_vals = self.env['res.partner'].play_onchanges(
            input_vals, ['parent_id']
        )
        self.assertIn('commercial_partner_id', updated_vals)
        self.assertIn('display_name', updated_vals)
        self.assertIn('partner_id', updated_vals)

    def test02_partner_country(self):
        partner_demo = self.env.ref('base.partner_demo')
        input_vals = {'partner_id': partner_demo.id}
        updated_vals = self.env['res.partner'].play_onchanges(
            input_vals, ['country_id']
        )
        self.assertIn('contact_address', updated_vals)
        self.assertIn('partner_id', updated_vals)

    def test_playing_onchange_on_model(self):
        result = self.env['res.partner'].play_onchanges(
            {'company_type': 'company'}, ['company_type']
        )
        self.assertEqual(result['is_company'], True)

    def test_playing_onchange_on_record(self):
        company = self.env.ref('base.main_company')
        result = company.play_onchanges(
            {'email': 'contact@akretion.com'}, ['email']
        )
        self.assertEqual(
            result['rml_footer'],
            u'Phone: +1 555 123 8069 | Email: contact@akretion.com | '
            u'Website: http://www.example.com',
        )
        self.assertEqual(company.email, u'info@yourcompany.example.com')
