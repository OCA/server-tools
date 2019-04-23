# -*- coding: utf-8 -*-
# © 2015 Guewen Baconnier (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp.tests.common as common


class TestActiveSearch(common.TransactionCase):

    def test_model_with_active_field(self):
        IrModel = self.env['ir.model']
        partner_model = IrModel.search([('model', '=', 'res.partner')],
                                       limit=1)
        self.assertTrue(partner_model.has_an_active_field)
        self.assertIn(partner_model,
                      IrModel.search([('has_an_active_field', '=', True)]))
        self.assertIn(partner_model,
                      IrModel.search([('has_an_active_field', '!=', False)]))
        self.assertNotIn(partner_model,
                         IrModel.search([('has_an_active_field', '!=', True)]))
        self.assertNotIn(partner_model,
                         IrModel.search([('has_an_active_field', '=', False)]))

    def test_model_without_active_field(self):
        IrModel = self.env['ir.model']
        country_model = IrModel.search([('model', '=', 'res.country')],
                                       limit=1)
        self.assertFalse(country_model.has_an_active_field)
        self.assertIn(country_model,
                      IrModel.search([('has_an_active_field', '!=', True)]))
        self.assertIn(country_model,
                      IrModel.search([('has_an_active_field', '=', False)]))
        self.assertNotIn(country_model,
                         IrModel.search([('has_an_active_field', '=', True)]))
        self.assertNotIn(country_model,
                         IrModel.search([('has_an_active_field', '!=', False)])
                         )
