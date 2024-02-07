# Copyright 2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from lxml import etree

from odoo.tests.common import TransactionCase


class TestBaseViewInheritanceExtension(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.maxDiff = None

    def test_base_view_inheritance_extension(self):
        view_id = self.env.ref("base.view_partner_simple_form").id
        arch, view = self.env["res.partner"]._get_view(view_id=view_id)
        # Verify normal attributes work
        self.assertEqual(arch.xpath("//form")[0].get("string"), "Partner form")
        # Verify our extra context key worked
        self.assertTrue(
            "'default_email': 'info@odoo-community.org'"
            in arch.xpath('//field[@name="parent_id"]')[0].get("context")
        )
        self.assertTrue(
            "'default_company_id': allowed_company_ids[0]"
            in arch.xpath('//field[@name="parent_id"]')[0].get("context")
        )

    def test_update_context_default(self):
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
                <attribute name="context" operation="update">
                    {"default_company_id": company_id}
                </attribute>
            </field>
            """
        )
        res = self.env["ir.ui.view"].apply_inheritance_specs(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="account_move_id"]')[0].attrib["context"],
            "{'default_journal_id': journal_id, 'default_company_id': company_id}",
        )

    def test_update_context_complex(self):
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
                <attribute name="context" operation="update">
                    {
                        "default_product_id": product_id,
                        "default_cost_center_id": (
                            context.get("handle_mrp_cost") and cost_center_id or False
                        ),
                    }
                </attribute>
            </field>
            """
        )
        res = self.env["ir.ui.view"].apply_inheritance_specs(source, specs)
        expected_items = [
            "'default_type': context.get('default_type')",
            "'journal_id': journal_id",
            "'default_partner_id': commercial_partner_id",
            (
                "'default_currency_id': "
                "currency_id != company_currency_id and currency_id or False"
            ),
            "'default_name': 'The company name'",
            "'default_product_id': product_id",
            (
                "'default_cost_center_id': "
                "context.get('handle_mrp_cost') and cost_center_id or False"
            ),
        ]
        self.assertEqual(
            res.xpath('//field[@name="invoice_line_ids"]')[0].attrib["context"],
            "{%s}" % ", ".join(expected_items),
        )

    def test_update_attrs_new_key(self):
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
                <attribute name="attrs" operation="update">
                    {
                        "required": [("state", "!=", "draft")],
                    }
                </attribute>
            </field>
            """
        )
        res = self.env["ir.ui.view"].apply_inheritance_specs(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="ref"]')[0].attrib["attrs"],
            "{'invisible': [('state', '=', 'draft')], "
            "'required': [('state', '!=', 'draft')]}",
        )

    def test_update_attrs_replace(self):
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
                <attribute name="attrs" operation="update">
                    {
                        "required": [('state', '!=', 'draft')],
                    }
                </attribute>
            </field>
            """
        )
        res = self.env["ir.ui.view"].apply_inheritance_specs(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="ref"]')[0].attrib["attrs"],
            "{'invisible': [('state', '=', 'draft')], "
            "'required': [('state', '!=', 'draft')]}",
        )

    def test_update_empty_source_dict(self):
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
                <attribute name="attrs" operation="update">
                    {
                        "required": [('state', '!=', 'draft')],
                    }
                </attribute>
            </field>
            """
        )
        res = self.env["ir.ui.view"].apply_inheritance_specs(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="ref"]')[0].attrib["attrs"],
            "{'required': [('state', '!=', 'draft')]}",
        )

    def test_update_operation_not_a_dict(self):
        """We should get an error if we try to update a dict with a non-dict spec"""
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
                <attribute name="attrs" operation="update">
                    ["not", "a", "dict"]
                </attribute>
            </field>
            """
        )
        with self.assertRaisesRegex(
            TypeError, "Operation for attribute `attrs` is not a dict"
        ):
            self.env["ir.ui.view"].apply_inheritance_specs(source, specs)

    def test_update_source_not_a_dict(self):
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
                <attribute name="domain" operation="update">
                    {
                        "required": [('state', '!=', 'draft')],
                    }
                </attribute>
            </field>
            """
        )
        with self.assertRaisesRegex(TypeError, "Attribute `domain` is not a dict"):
            self.env["ir.ui.view"].apply_inheritance_specs(source, specs)

    def test_attrs_domain_add_join_operator_or(self):
        """Test that we can add an OR domain to an existing attrs key."""
        self._test_attrs_domain_add(join_operator="OR")

    def test_attrs_domain_add_join_operator_and(self):
        """Test that we can add an AND domain to an existing attrs key."""
        self._test_attrs_domain_add(join_operator="AND")

    def _test_attrs_domain_add(self, join_operator):
        """Test that we can add a domain to an existing attrs domain key."""
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
                <attribute name="attrs" operation="attrs_domain_add"
                           key="required" join_operator="%s">
                    [('state', '!=', 'draft')]
                </attribute>
            </field>
            """
            % (join_operator,)
        )
        res = self.env["ir.ui.view"].apply_inheritance_specs(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="ref"]')[0].attrib["attrs"],
            "{'invisible': [('state', '=', 'draft')], "
            "'required': ['%s', ('state', '=', False), ('state', '!=', 'draft')]}"
            % ("|" if join_operator == "OR" else "&"),
        )

    def test_attrs_domain_add_no_attrs(self):
        """Test attrs_domain_add if there is no attrs: attrs is created."""
        source = etree.fromstring(
            """
            <form>
                <field name="ref"/>
            </form>
            """
        )
        specs = etree.fromstring(
            """
            <field name="ref" position="attributes">
                <attribute name="attrs" operation="attrs_domain_add"
                           key="required" join_operator="OR">
                    [('state', '!=', 'draft')]
                </attribute>
            </field>
            """
        )
        res = self.env["ir.ui.view"].apply_inheritance_specs(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="ref"]')[0].attrib["attrs"],
            "{'required': [('state', '!=', 'draft')]}",
        )
