# Copyright 2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from lxml import etree

from odoo.tests.common import SavepointCase


class TestBaseViewInheritanceExtension(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ViewModel = cls.env["ir.ui.view"]

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
            source, specs
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
            source, specs
        )
        button_node = modified_source.xpath('//button[@name="test"]')[0]
        self.assertEqual(button_node.attrib["states"], "draft,open,valid,payable,paid")

    def test_list_remove(self):
        view_model = self.env["ir.ui.view"]
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
            source, specs
        )
        button_node = modified_source.xpath('//button[@name="test"]')[0]
        self.assertEqual(button_node.attrib["states"], "draft,valid,paid")

    def test_python_dict_inheritance_context_default(self):
        source = etree.fromstring(
            """
            <form>
                <field name="account_move_id" context="{'default_journal_id': journal_id}" />
            </form>
            """
        )
        specs = etree.fromstring(
            """
            <field name="account_move_id" position="attributes">
                <attribute name="context" operation="python_dict" key="default_company_id">
                    company_id
                </attribute>
            </field>
            """
        )
        res = self.ViewModel.inheritance_handler_attributes_python_dict(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="account_move_id"]')[0].attrib["context"],
            "{'default_journal_id': journal_id, 'default_company_id': company_id}",
        )

    def test_python_dict_inheritance_context_complex(self):
        source = etree.fromstring(
            """
            <form>
                <field
                    name="invoice_line_ids"
                    context="{
                        'default_type': context.get('default_type'),
                        'journal_id': journal_id,
                        'default_partner_id': commercial_partner_id,
                        'default_currency_id': (
                            currency_id != company_currency_id and currency_id or False
                        ),
                        'default_name': 'The company name',
                    }"
                />
            </form>
            """
        )
        specs = etree.fromstring(
            """
            <field name="invoice_line_ids" position="attributes">
                <attribute name="context" operation="python_dict" key="default_product_id">
                    product_id
                </attribute>
                <attribute name="context" operation="python_dict" key="default_cost_center_id">
                    context.get('handle_mrp_cost') and cost_center_id or False
                </attribute>
            </field>
            """
        )
        res = self.ViewModel.inheritance_handler_attributes_python_dict(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="invoice_line_ids"]')[0].attrib["context"],
            "{'default_type': context.get('default_type'), 'journal_id': journal_id, "
            "'default_partner_id': commercial_partner_id, 'default_currency_id': "
            "currency_id != company_currency_id and currency_id or False, "
            "'default_name': 'The company name', 'default_product_id': product_id, "
            "'default_cost_center_id': context.get('handle_mrp_cost') and "
            "cost_center_id or False}",
        )

    def test_python_dict_inheritance_attrs_add(self):
        """Test that we can add new keys to an existing dict"""
        source = etree.fromstring(
            """
            <form>
                <field
                    name="ref"
                    attrs="{'invisible': [('state', '=', 'draft')]}"
                />
            </form>
            """
        )
        specs = etree.fromstring(
            """
            <field name="ref" position="attributes">
                <attribute name="attrs" operation="python_dict" key="required">
                    [('state', '!=', 'draft')]
                </attribute>
            </field>
            """
        )
        res = self.ViewModel.inheritance_handler_attributes_python_dict(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="ref"]')[0].attrib["attrs"],
            "{'invisible': [('state', '=', 'draft')], "
            "'required': [('state', '!=', 'draft')]}",
        )

    def test_python_dict_inheritance_attrs_update(self):
        """Test that we can replace an existing dict key"""
        source = etree.fromstring(
            """
            <form>
                <field
                    name="ref"
                    attrs="{
                        'invisible': [('state', '=', 'draft')],
                        'required': [('state', '=', False)],
                    }"
                />
            </form>
            """
        )
        specs = etree.fromstring(
            """
            <field name="ref" position="attributes">
                <attribute name="attrs" operation="python_dict" key="required">
                    [('state', '!=', 'draft')]
                </attribute>
            </field>
            """
        )
        res = self.ViewModel.inheritance_handler_attributes_python_dict(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="ref"]')[0].attrib["attrs"],
            "{'invisible': [('state', '=', 'draft')], "
            "'required': [('state', '!=', 'draft')]}",
        )

    def test_python_dict_inheritance_attrs_new(self):
        """Test that we can add new keys by creating the dict if it's missing"""
        source = etree.fromstring(
            """
            <form>
                <field name="ref" />
            </form>
            """
        )
        specs = etree.fromstring(
            """
            <field name="ref" position="attributes">
                <attribute name="attrs" operation="python_dict" key="required">
                    [('state', '!=', 'draft')]
                </attribute>
            </field>
            """
        )
        res = self.ViewModel.inheritance_handler_attributes_python_dict(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="ref"]')[0].attrib["attrs"],
            "{'required': [('state', '!=', 'draft')]}",
        )

    def test_python_dict_inheritance_attrs_missing_key(self):
        """We should get an error if we try to update a dict without specifing a key"""
        source = etree.fromstring(
            """
            <form>
                <field name="ref" />
            </form>
            """
        )
        specs = etree.fromstring(
            """
            <field name="ref" position="attributes">
                <attribute name="attrs" operation="python_dict">
                    [('state', '!=', 'draft')]
                </attribute>
            </field>
            """
        )
        with self.assertRaisesRegex(
            AssertionError, "No key specified for 'python_dict' operation"
        ):
            self.ViewModel.inheritance_handler_attributes_python_dict(source, specs)

    def test_python_dict_inheritance_error_if_not_a_dict(self):
        """We should get an error if we try to update a non-dict attribute"""
        source = etree.fromstring(
            """
            <form>
                <field name="child_ids" domain="[('state', '=', 'confirm')]" />
            </form>
            """
        )
        specs = etree.fromstring(
            """
            <field name="child_ids" position="attributes">
                <attribute name="domain" operation="python_dict" key="required">
                    [('state', '!=', 'draft')]
                </attribute>
            </field>
            """
        )
        with self.assertRaisesRegex(AssertionError, "'domain' is not a dict"):
            self.ViewModel.inheritance_handler_attributes_python_dict(source, specs)
