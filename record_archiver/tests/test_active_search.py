# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#


import openerp.tests.common as common


class TestActiveSearch(common.TransactionCase):

    def test_model_with_active_field(self):
        cr, uid = self.cr, self.uid
        IrModel = self.registry('ir.model')
        partner_model_id = IrModel.search(cr, uid,
                                          [('model', '=', 'res.partner')],
                                          limit=1)[0]
        partner_model = IrModel.browse(cr, uid, partner_model_id)
        self.assertTrue(partner_model.has_an_active_field)
        self.assertIn(partner_model_id,
                      IrModel.search(cr, uid,
                                     [('has_an_active_field', '=', True)]))
        self.assertIn(partner_model_id,
                      IrModel.search(cr, uid,
                                     [('has_an_active_field', '!=', False)]))

    def test_model_without_active_field(self):
        cr, uid = self.cr, self.uid
        IrModel = self.registry('ir.model')
        country_model_id = IrModel.search(cr, uid,
                                          [('model', '=', 'res.country')],
                                          limit=1)
        country_model = IrModel.browse(cr, uid, country_model_id[0])
        self.assertFalse(country_model.has_an_active_field)
        self.assertNotIn(country_model_id,
                         IrModel.search(cr, uid,
                                        [('has_an_active_field', '=', False)]))
        self.assertNotIn(country_model_id,
                         IrModel.search(cr, uid,
                                        [('has_an_active_field', '!=', True)]))
