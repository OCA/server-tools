# -*- coding: utf-8 -*-
from openerp import api
from openerp.exceptions import AccessError
from openerp.tests import common
from lxml import etree


class TestBaseTechnicalFeatures(common.TransactionCase):

    def test_01_visible_menus(self):
        """ A technical feature is visible to the user with the technical \
        features group """
        menu_obj = self.env['ir.ui.menu'].with_context(
            {'ir.ui.menu.full_list': True})
        menu_id = menu_obj.search(
            [('groups_id', '=', self.env.ref('base.group_no_one').id)],
            limit=1).id
        self.env.user.write({'technical_features': False})
        self.assertNotIn(menu_id, menu_obj._visible_menu_ids())
        self.env.user.write({'technical_features': True})
        self.assertIn(menu_id, menu_obj._visible_menu_ids())

    def test02_visible_fields(self):
        """ A technical field is visible when its form is loaded by a user \
        with the technical features group """

        def get_partner_field_invisible():
            xml = etree.fromstring(
                self.env['res.users'].fields_view_get(
                    view_id=self.env.ref('base.view_users_form').id
                )['arch'].encode('utf-8'))
            return xml.xpath(
                '//div/group/field[@name="partner_id"]')[0].get('invisible')

        self.env.user.write({'technical_features': False})
        self.assertEqual(get_partner_field_invisible(), '1')
        self.env.user.write({'technical_features': True})
        self.assertEqual(get_partner_field_invisible(), None)

    def test03_user_access(self):
        """ Setting the user pref raises an access error if the user is not \
        in group_no_one """
        user = self.env['res.users'].create({
            'name': 'Test user technical features',
            'login': 'testusertechnicalfeatures',
            'groups_id': [(6, 0, [])]})
        with api.Environment.manage():
            env = api.Environment(
                self.env.cr, user.id, self.env.context)
            with self.assertRaises(AccessError):
                env['res.users'].browse(user.id).write(
                    {'technical_features': True})
        with self.assertRaises(AccessError):
            user.write({'technical_features': True})
        user.write({'groups_id': [(4, self.env.ref('base.group_no_one').id)]})
        with api.Environment.manage():
            env = api.Environment(
                self.env.cr, user.id, self.env.context)
            env['res.users'].browse(user.id).write({
                'technical_features': True})
