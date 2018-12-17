# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestOnchangeHelper(TransactionCase):
    def test01_partner_parent(self):
        main_partner = self.env.ref('base.main_partner')
        input_vals = dict(parent_id=main_partner.id, type='contact')
        updated_vals = self.env['res.partner'].play_onchanges(
            input_vals, ['parent_id']
        )
        self.assertIn('country_id', updated_vals)
        self.assertIn('state_id', updated_vals)
        self.assertIn('street', updated_vals)
        self.assertIn('zip', updated_vals)

        self.assertEqual(
            updated_vals['country_id'], main_partner.country_id.id
        )
        self.assertEqual(updated_vals['state_id'], main_partner.state_id.id)
        self.assertEqual(updated_vals['street'], main_partner.street)
        self.assertEqual(updated_vals['zip'], main_partner.zip)

    def test02_partner_country(self):
        partner_demo = self.env.ref('base.partner_demo')
        input_vals = {'country_id': self.env.ref('base.us').id}
        updated_vals = partner_demo.play_onchanges(input_vals, ['country_id'])
        self.assertIn('country_id', updated_vals)

    def test_playing_onchange_on_model(self):
        result = self.env['res.partner'].play_onchanges(
            {'company_type': 'company'}, ['company_type']
        )
        self.assertEqual(result['is_company'], True)
