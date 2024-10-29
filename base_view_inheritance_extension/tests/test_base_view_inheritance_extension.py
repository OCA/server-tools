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
        arch, _ = self.env["res.partner"]._get_view(view_id=view_id)
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
                <field name="account_move_id"
                 context="{'default_journal_id': journal_id}" />
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
            "{%s}" % ", ".join(expected_items),  # noqa: UP031
        )

    def test_text_add_operation(self):
        source = etree.fromstring(
            """
            <form>
                <field name="customer_id" string="Client"/>
            </form>
            """
        )

        specs = etree.fromstring(
            """
            <field name="customer_id" position="attributes">
                <attribute name="string"
                operation="text_add">{old_value} Customer</attribute>
            </field>
            """
        )

        res = self.env["ir.ui.view"].apply_inheritance_specs(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="customer_id"]')[0].attrib["string"],
            "Client Customer",
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
                <attribute name="context" operation="update">
                    ["not", "a", "dict"]
                </attribute>
            </field>
            """
        )
        with self.assertRaisesRegex(
            TypeError, "Operation for attribute `context` is not a dict"
        ):
            self.env["ir.ui.view"].apply_inheritance_specs(source, specs)

    def test_domain_add_operation(self):
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
                <attribute name="domain" operation="domain_add">
                    [('state', '!=', 'draft')]
                </attribute>
            </field>
            """
        )
        res = self.env["ir.ui.view"].apply_inheritance_specs(source, specs)
        self.assertEqual(
            res.xpath('//field[@name="child_ids"]')[0].attrib["domain"],
            "['&', ('state', '=', 'confirm'), ('state', '!=', 'draft')]",
        )

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
