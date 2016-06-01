# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C):
#        2012-Today Serpent Consulting Services (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.tests import common


class TestMassEditing(common.TransactionCase):

    def setUp(self):
        super(TestMassEditing, self).setUp()
        self.mass_object_model = self.env['mass.object']
        self.res_partner_model = self.env['res.partner']
        self.partner = self._create_partner()
        self.partner_model = self.env['ir.model'].\
            search([('model', '=', 'res.partner')])
        self.fields_model = self.env['ir.model.fields'].\
            search([('model', '=', 'res.partner'), ('name', '=', 'email')])
        self._create_mass_editing(self.partner_model, self.fields_model)

    def _create_partner(self):
        """Create a Partner."""
        partner = self.res_partner_model.create({
            'name': 'Test Partner',
            'email': 'example@yourcompany.com',
        })
        return partner

    def _create_mass_editing(self, model, field):
        """Create a Mass Editing with Partner as model and
        email field of partner."""
        mass = self.mass_object_model.create({
            'name': 'Mass Editing for Partner',
            'model_id': model.id,
            'field_ids': [(6, 0, [field.id])]
        })
        mass.create_action()

    def _apply_action_remove(self, partner):
        """Create Wizard object to perform mass editing to
        REMOVE email field's value."""
        partner_context = {
            'active_id': partner.id,
            'active_ids': partner.ids,
            'active_model': 'res.partner',
        }
        self.env['mass.editing.wizard'].with_context(partner_context).create({
            'selection__email': 'remove'
        })
        return True

    def _apply_action_set(self, partner):
        """Create Wizard object to perform mass editing to
        SET email field's value."""
        partner_context = {
            'active_id': partner.id,
            'active_ids': partner.ids,
            'active_model': 'res.partner',
        }
        self.env['mass.editing.wizard'].with_context(partner_context).create({
            'selection__email': 'set',
            'email': 'sample@mycompany.com'
        })
        return True

    def test_security(self):
        """Test Case for MASS EDITING which will remove and after add
        Partner's email and will assert the same."""
        self._apply_action_remove(self.partner)
        self.assertEqual(self.partner.email, False,
                         'Partner\'s Email should be removed.')
        self._apply_action_set(self.partner)
        self.assertNotEqual(self.partner.email, False,
                            'Partner\'s Email should be set.')
