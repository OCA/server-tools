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
