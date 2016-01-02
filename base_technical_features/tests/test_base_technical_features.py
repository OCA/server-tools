# -*- coding: utf-8 -*-
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
        self.env.user.groups_id -= self.env.ref(
            'base_technical_features.group_technical_features')
        self.assertNotIn(menu_id, menu_obj._visible_menu_ids())
        self.env.user.groups_id += self.env.ref(
            'base_technical_features.group_technical_features')
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

        self.env['basemodel.monkeypatch']._register_hook()
        self.env.user.groups_id -= self.env.ref(
            'base_technical_features.group_technical_features')
        self.assertEqual(get_partner_field_invisible(), '1')
        self.env.user.write({'groups_id': [(4, self.env.ref(
            'base_technical_features.group_technical_features').id)]})
        self.assertEqual(get_partner_field_invisible(), None)
