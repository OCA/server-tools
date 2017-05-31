# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from openerp.tests import common
from openerp.modules import registry
from openerp.addons.mass_editing.hooks import uninstall_hook


class TestMassEditing(common.TransactionCase):

    def setUp(self):
        super(TestMassEditing, self).setUp()
        model_obj = self.env['ir.model']
        self.mass_wiz_obj = self.env['mass.editing.wizard']
        self.mass_object_model = self.env['mass.object']
        self.res_partner_model = self.env['res.partner']
        self.ir_translation_model = self.env['ir.translation']
        self.lang_model = self.env['res.lang']

        self.partner = self._create_partner()
        self.partner_model = model_obj.\
            search([('model', '=', 'res.partner')])
        self.user_model = model_obj.search([('model', '=', 'res.users')])
        self.fields_model = self.env['ir.model.fields'].\
            search([('model_id', '=', self.partner_model.id),
                    ('name', 'in', ['email', 'phone', 'category_id', 'comment',
                                    'country_id', 'customer', 'child_ids',
                                    'title'])])
        self.mass = self._create_mass_editing(self.partner_model,
                                              self.fields_model,
                                              'Partner')
        self.copy_mass = self.mass.copy()
        self.user = self._create_user()

        self.res_partner_title_model = self.env['res.partner.title']
        self.partner_title = self._create_partner_title()
        self.partner_title_model = model_obj.\
            search([('model', '=', 'res.partner.title')])
        self.fields_partner_title_model = self.env['ir.model.fields']. \
            search([('model_id', '=', self.partner_title_model.id),
                    ('name', 'in', ['abbreviation'])])
        self.mass_partner_title = self._create_mass_editing(
                                            self.partner_title_model,
                                            self.fields_partner_title_model,
                                            'Partner Title')

    def _create_partner(self):
        """Create a Partner."""
        categ_ids = self.env['res.partner.category'].search([]).ids
        return self.res_partner_model.create({
            'name': 'Test Partner',
            'email': 'example@yourcompany.com',
            'phone': 123456,
            'category_id': [(6, 0, categ_ids)],
            'notify_email': 'always'
        })

    def _create_partner_title(self):
        """Create a Partner Title."""
        # Loads German to work with translations
        self.lang_model.load_lang('de_DE')

        partner_title = self.res_partner_title_model.create({
            'name': 'Ambassador',
            'shortcut': 'Amb.',
        })
        # Adding translated terms
        ctx = {'lang':'de_DE'}
        partner_title.with_context(ctx).write({'name': 'Botschafter',
                                               'shortcut': 'Bots.'})
        return partner_title

    def _create_user(self):
        return self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_login',
            'email': 'test@test.com',
        })

    def _create_mass_editing(self, model, fields, model_name):
        """Create a Mass Editing with Partner as model and
        email field of partner."""
        mass = self.mass_object_model.create({
            'name': u'Mass Editing for {0}'.format(model_name),
            'model_id': model.id,
            'field_ids': [(6, 0, fields.ids)]
        })
        mass.create_action()
        return mass

    def _apply_action(self, obj, vals):
        """Create Wizard object to perform mass editing to
        REMOVE field's value."""
        ctx = {
            'active_id': obj.id,
            'active_ids': obj.ids,
            'active_model': obj._name,
        }
        return self.mass_wiz_obj.with_context(ctx).create(vals)

    def test_wiz_fields_view_get(self):
        """Test whether fields_view_get method returns arch or not."""
        ctx = {
            'mass_editing_object': self.mass.id,
            'active_id': self.partner.id,
            'active_ids': self.partner.ids,
            'active_model': 'res.partner',
        }
        result = self.mass_wiz_obj.with_context(ctx).fields_view_get()
        self.assertTrue(result.get('arch'),
                        'Fields view get must return architecture.')
        fields = result.get("fields")
        self.assertTrue(fields)
        for name, values in fields.items():
            self.assertTrue(isinstance(values["views"], dict))

    def test_onchange_model(self):
        """Test whether onchange model_id returns model_id in list"""
        new_mass = self.mass_object_model.new({'model_id': self.user_model.id})
        new_mass._onchange_model_id()
        model_list = ast.literal_eval(new_mass.model_list)
        self.assertTrue(self.user_model.id in model_list,
                        'Onchange model list must contains model_id.')

    def test_mass_edit_partner_title(self):
        """Test Case for MASS EDITING which will check if translation
        was loaded for new partner title, and if they are removed
        as well as the value for the abbreviation for the partner title."""

        search_domain = [('res_id', '=', self.partner_title.id),
                         ('type', '=', 'model'),
                         ('name', '=', 'res.partner.title,shortcut'),
                         ('lang', '=', 'de_DE')]

        translation_ids = self.ir_translation_model.search(search_domain)

        self.assertEqual(len(translation_ids), 1,
                         'Translation for Partner Title\'s Abbreviation '
                         'was not loaded properly.')

        vals = {
            'selection__shortcut': 'remove',
        }
        self._apply_action(self.partner_title, vals)
        self.assertEqual(self.partner_title.shortcut, False,
                         'Partner Title\'s Abbreviation should be removed.')

        translation_ids = self.ir_translation_model.search(search_domain)

        self.assertEqual(len(translation_ids), 0,
                         'Translation for Partner Title\'s Abbreviation '
                         'was not removed properly.')

    def test_mass_edit_email(self):
        """Test Case for MASS EDITING which will remove and after add
        Partner's email and will assert the same."""
        # Remove email address
        vals = {
            'selection__email': 'remove',
            'selection__phone': 'remove',
        }
        self._apply_action(self.partner, vals)
        self.assertEqual(self.partner.email, False,
                         'Partner\'s Email should be removed.')
        # Set email address
        vals = {
            'selection__email': 'set',
            'email': 'sample@mycompany.com',
        }
        self._apply_action(self.partner, vals)
        self.assertNotEqual(self.partner.email, False,
                            'Partner\'s Email should be set.')

    def test_mass_edit_m2m_categ(self):
        """Test Case for MASS EDITING which will remove and add
        Partner's category m2m."""
        # Remove m2m categories
        vals = {
            'selection__category_id': 'remove_m2m',
        }
        self._apply_action(self.partner, vals)
        self.assertNotEqual(self.partner.category_id, False,
                            'Partner\'s category should be removed.')
        # Add m2m categories
        dist_categ_id = self.env.ref('base.res_partner_category_13').id
        vals = {
            'selection__category_id': 'add',
            'category_id': [[6, 0, [dist_categ_id]]],
        }
        wiz_action = self._apply_action(self.partner, vals)
        self.assertTrue(dist_categ_id in self.partner.category_id.ids,
                        'Partner\'s category should be added.')
        # Check window close action
        res = wiz_action.action_apply()
        self.assertTrue(res['type'] == 'ir.actions.act_window_close',
                        'IR Action must be window close.')

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

    def test_unlink_mass(self):
        """Test if related actions are removed when mass editing
        record is unlinked."""
        mass_action_id = "ir.actions.act_window," + str(self.mass.id)
        self.mass.unlink()
        value_cnt = self.env['ir.values'].search([('value', '=',
                                                   mass_action_id)],
                                                 count=True)
        self.assertTrue(value_cnt == 0,
                        "Sidebar action must be removed when mass"
                        " editing is unlinked.")

    def test_uninstall_hook(self):
        """Test if related actions are removed when mass editing
        record is uninstalled."""
        uninstall_hook(self.cr, registry)
        mass_action_id = "ir.actions.act_window," + str(self.mass.id)
        value_cnt = self.env['ir.values'].search([('value', '=',
                                                   mass_action_id)],
                                                 count=True)
        self.assertTrue(value_cnt == 0,
                        "Sidebar action must be removed when mass"
                        " editing module is uninstalled.")
