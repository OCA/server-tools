# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from lxml import etree
from openerp.tests.common import TransactionCase


class TestBaseViewInheritanceExtension(TransactionCase):

    def test_base_view_inheritance_extension(self):
        view_id = self.env.ref('base.view_partner_form').id
        fields_view_get = self.env['res.partner'].fields_view_get(
            view_id=view_id
        )
        view = etree.fromstring(fields_view_get['arch'])
        # verify normal attributes work
        self.assertEqual(view.xpath('//form')[0].get('string'), 'Partner form')
        # verify our extra context key worked
        self.assertTrue(
            'default_name' in
            view.xpath('//field[@name="parent_id"]')[0].get('context')
        )
        self.assertTrue(
            "context.get('company_id', context.get('company'))" in
            view.xpath('//field[@name="parent_id"]')[0].get('context')
        )
        # verify we moved the child_ids field
        self.assertEqual(
            view.xpath('//field[@name="child_ids"]')[0].getparent(),
            view.xpath('//page[@name="my_new_page"]')[0]
        )

    def test_list_add(self):
        view_model = self.env['ir.ui.view']
        inherit_id = self.env.ref('base.view_partner_form').id
        source = etree.fromstring(
            """\
            <form>
                <button name="test" states="draft,open"/>
            </form>
            """
        )
        # extend with single value
        specs = etree.fromstring(
            """\
            <button name="test" position="attributes">
                <attribute
                    name="states"
                    operation="list_add"
                    >valid</attribute>
            </button>
            """
        )
        modified_source = \
            view_model.inheritance_handler_attributes_list_add(
                source, specs, inherit_id
            )
        button_node = modified_source.xpath('//button[@name="test"]')[0]
        self.assertEqual(
            button_node.attrib['states'],
            'draft,open,valid'
        )
        # extend with list of values
        specs = etree.fromstring(
            """\
            <button name="test" position="attributes">
                <attribute
                    name="states"
                    operation="list_add"
                    >payable,paid</attribute>
            </button>
            """
        )
        modified_source = \
            view_model.inheritance_handler_attributes_list_add(
                source, specs, inherit_id
            )
        button_node = modified_source.xpath('//button[@name="test"]')[0]
        self.assertEqual(
            button_node.attrib['states'],
            'draft,open,valid,payable,paid'
        )

    def test_list_remove(self):
        view_model = self.env['ir.ui.view']
        inherit_id = self.env.ref('base.view_partner_form').id
        source = etree.fromstring(
            """\
            <form>
                <button name="test" states="draft,open,valid,payable,paid"/>
            </form>
            """
        )
        # remove list of values
        specs = etree.fromstring(
            """\
            <button name="test" position="attributes">
                <attribute
                    name="states"
                    operation="list_remove"
                    >open,payable</attribute>
            </button>
            """
        )
        modified_source = \
            view_model.inheritance_handler_attributes_list_remove(
                source, specs, inherit_id
            )
        button_node = modified_source.xpath('//button[@name="test"]')[0]
        self.assertEqual(
            button_node.attrib['states'],
            'draft,valid,paid'
        )

    def test_user_ids(self):
        view_id = self.env.ref('base.view_partner_form').id
        demo_marker = 'I am a private form for the demo user'
        fields_view_get = self.env['res.partner'].fields_view_get(
            view_id=view_id
        )
        self.assertNotIn(demo_marker, fields_view_get['arch'])
        fields_view_get = self.env['res.partner'].sudo(
            self.env.ref('base.user_demo')
        ).fields_view_get(
            view_id=view_id
        )
        self.assertIn(demo_marker, fields_view_get['arch'])

    def test_view_delete_deactivate(self):
        """
        This function tests that the views are deleted and deactivated when
        and if the single user they have been assigned to is deleted or
        deactivated accordingly.
        """
        model_res_users = self.env['res.users']
        model_ir_ui_view = self.env['ir.ui.view']
        user1 = model_res_users.create({'login': 'user1', 'name': 'user1'})
        user2 = model_res_users.create({'login': 'user2', 'name': 'user2'})
        user3 = model_res_users.create({'login': 'user3', 'name': 'user3'})
        user4 = model_res_users.create({
            'login': 'user4',
            'name': 'user4',
            'active': False,
        })
        view1 = self.env.ref('base.view_partner_form')
        view2 = model_ir_ui_view.create({
            'name': 'view2',
            'model': 'res.partner',
            'inherit_id': view1.id,
            'arch': '<div></div>',
            'user_ids': [(6, False, user2.ids)]
        })
        view3 = model_ir_ui_view.create({
            'name': 'view3',
            'model': 'res.partner',
            'inherit_id': view1.id,
            'arch': '<div></div>',
            'user_ids': [(6, False, user2.ids + user1.ids + user3.ids)]
        })
        view4 = model_ir_ui_view.create({
            'name': 'view4',
            'model': 'res.partner',
            'inherit_id': view1.id,
            'arch': '<div></div>',
        })
        view5 = model_ir_ui_view.create({
            'name': 'view5',
            'model': 'res.partner',
            'inherit_id': view1.id,
            'arch': '<div></div>',
            'user_ids': [(6, False, user3.ids + user4.ids)],
        })
        # delete user2, make sure that only view2 is deleted
        self.assertTrue(view1.exists())
        self.assertTrue(view2.exists())
        self.assertTrue(view3.exists())
        self.assertTrue(view4.exists())
        self.assertTrue(view5.exists())
        user2.unlink()
        self.assertTrue(view1.exists())
        self.assertFalse(view2.exists())
        self.assertTrue(view3.exists())
        self.assertTrue(view4.exists())
        self.assertTrue(view5.exists())
        # deactivate user3, make sure that only view5 is deactivated
        self.assertTrue(view1.active)
        self.assertTrue(view3.active)
        self.assertTrue(view4.active)
        self.assertTrue(view5.active)
        user3.write({'active': False})
        self.assertTrue(view1.active)
        self.assertTrue(view3.active)
        self.assertTrue(view4.active)
        self.assertFalse(view5.active)
