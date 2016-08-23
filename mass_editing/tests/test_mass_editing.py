# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
            search([('model', '=', self.partner_model.model),
                    ('name', '=', 'email')])
        self.mass = self._create_mass_editing(self.partner_model,
                                              self.fields_model)
        self.copy_mass = self.mass.copy()

    def _create_partner(self):
        """Create a Partner."""
        return self.res_partner_model.create({
            'name': 'Test Partner',
            'email': 'example@yourcompany.com',
        })

    def _create_mass_editing(self, model, field):
        """Create a Mass Editing with Partner as model and
        email field of partner."""
        mass = self.mass_object_model.create({
            'name': 'Mass Editing for Partner',
            'model_id': model.id,
            'field_ids': [(6, 0, [field.id])]
        })
        mass.create_action()
        return mass

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
            'email': 'sample@mycompany.com',
        })
        return True

    def test_mass_edit(self):
        """Test Case for MASS EDITING which will remove and after add
        Partner's email and will assert the same."""
        self._apply_action_remove(self.partner)
        self.assertEqual(self.partner.email, False,
                         'Partner\'s Email should be removed.')
        self._apply_action_set(self.partner)
        self.assertNotEqual(self.partner.email, False,
                            'Partner\'s Email should be set.')

    def test_mass_edit_copy(self):
        """Test if fields one2many field gets blank when mass editing record
        is copied.
        """
        self.assertEqual(self.copy_mass.field_ids.ids, [],
                         'Fields must be blank.')

    def test_sidebar_action(self):
        """Test if Sidebar Action is added / removed to / from give object."""
        action = self.mass.ref_ir_act_window_id and self.mass.ref_ir_value_id
        self.assertTrue(action, 'Sidebar action must be exists.')
        # Remove the sidebar actions
        self.mass.unlink_action()
        action = self.mass.ref_ir_act_window_id and self.mass.ref_ir_value_id
        self.assertFalse(action, 'Sidebar action must be removed.')
