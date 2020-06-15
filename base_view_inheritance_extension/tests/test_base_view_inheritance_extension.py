# Copyright 2016 Therp BV <http://therp.nl>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from lxml import etree

from odoo.tests.common import TransactionCase


class TestBaseViewInheritanceExtension(TransactionCase):
    def test_base_view_inheritance_extension(self):
        view_id = self.env.ref("base.view_partner_simple_form").id
        fields_view_get = self.env["res.partner"].fields_view_get(view_id=view_id)
        view = etree.fromstring(fields_view_get["arch"])
        # verify normal attributes work
        self.assertEqual(view.xpath("//form")[0].get("string"), "Partner form")
        # verify our extra context key worked
        self.assertTrue(
            "default_name" in view.xpath('//field[@name="parent_id"]')[0].get("context")
        )
        self.assertTrue(
            "context.get('company_id', context.get('company'))"
            in view.xpath('//field[@name="parent_id"]')[0].get("context")
        )

    def test_list_add(self):
        view_model = self.env["ir.ui.view"]
        inherit_id = self.env.ref("base.view_partner_form").id
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
        modified_source = view_model.inheritance_handler_attributes_list_add(
            source, specs, inherit_id
        )
        button_node = modified_source.xpath('//button[@name="test"]')[0]
        self.assertEqual(button_node.attrib["states"], "draft,open,valid")
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
        modified_source = view_model.inheritance_handler_attributes_list_add(
            source, specs, inherit_id
        )
        button_node = modified_source.xpath('//button[@name="test"]')[0]
        self.assertEqual(button_node.attrib["states"], "draft,open,valid,payable,paid")

    def test_list_remove(self):
        view_model = self.env["ir.ui.view"]
        inherit_id = self.env.ref("base.view_partner_form").id
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
        modified_source = view_model.inheritance_handler_attributes_list_remove(
            source, specs, inherit_id
        )
        button_node = modified_source.xpath('//button[@name="test"]')[0]
        self.assertEqual(button_node.attrib["states"], "draft,valid,paid")

    def test_python_dict_inheritance(self):
        view_model = self.env["ir.ui.view"]
        inherit_id = self.env.ref("base.view_partner_form").id
        source = etree.fromstring(
            """<form>
                <field name="invoice_line_ids"
                    context="{
                    'default_type': context.get('default_type'),
                    'journal_id': journal_id,
                    'default_partner_id': commercial_partner_id,
                    'default_currency_id':
                    currency_id != company_currency_id and currency_id or False,
                    'default_name': 'The company name',
                    }"/>
            </form>"""
        )
        specs = etree.fromstring(
            """\
            <field name="invoice_line_ids" position="attributes">
                <attribute name="context" operation="python_dict"
                    key="my_key">my_value</attribute>
                <attribute name="context" operation="python_dict"
                    key="my_key2">'my name'</attribute>
                <attribute name="context" operation="python_dict"
                 key="default_cost_center_id">cost_center_id</attribute>
            </field>
            """
        )
        modified_source = view_model.inheritance_handler_attributes_python_dict(
            source, specs, inherit_id
        )
        field_node = modified_source.xpath('//field[@name="invoice_line_ids"]')[0]
        self.assertTrue(
            "currency_id != company_currency_id and currency_id or False"
            in field_node.attrib["context"]
        )
        self.assertTrue("my_value" in field_node.attrib["context"])
        self.assertFalse("'cost_center_id'" in field_node.attrib["context"])
