# Copyright 2016 Therp BV <https://therp.nl>
# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from lxml import etree

from odoo.tests.common import SavepointCase
from odoo.tools.safe_eval import safe_eval


class TestBaseViewInheritanceExtension(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ViewModel = cls.env["ir.ui.view"]

    def test_partner_view_full_validation(self):
        view = self.env.ref(
            "base_view_inheritance_extension.view_partner_simple_form_2"
        )
        view.active = True
        res = self.env["res.partner"].fields_view_get()
        arch = etree.XML(res["arch"])
        # Test adding domain to attribute
        country_id = arch.xpath("//field[@name='country_id']")[0]
        self.assertEqual(country_id.get("domain"), "[('code', '=', 'es')]")
        # Test adding text to attribute
        mobile = arch.xpath("//field[@name='mobile']")[0]
        self.assertIn("Pre-", mobile.get("string"))
        # Test adding key in context dict
        parent = arch.xpath("//field[@name='parent_id']")[0]
        self.assertIn("default_company_id", parent.get("context"))
        self.assertIn("default_is_company", parent.get("context"))
        # Test adding key inside existing dict
        function = arch.xpath("//field[@name='function']")[0]
        f_dict = safe_eval(function.get("attrs"))
        self.assertEqual([("is_company", "=", False)], f_dict["required"])
        self.assertEqual([("is_company", "=", True)], f_dict["invisible"])
        # Test replacing dict key
        email = arch.xpath("//field[@name='email']")[0]
        e_dict = safe_eval(email.get("attrs"))
        self.assertEqual([("is_company", "=", False)], e_dict["required"])
        # Test adding keys if dict is missing
        mobile_dict = safe_eval(mobile.get("attrs"))
        self.assertEqual([("is_company", "=", False)], mobile_dict["invisible"])
        # Test complex context
        state = arch.xpath("//field[@name='state_id']")[0]
        self.assertIn(
            "'default_country_id': context.get('force_country_id') and country_id or False",
            state.get("context"),
        )

    def test_list_add_remove(self):
        view = self.env.ref("base_view_inheritance_extension.view_user_simple_form")
        view.active = True
        res = self.env["res.users"].fields_view_get(
            view_id=self.env.ref("base.view_users_form").id
        )
        arch = etree.XML(res["arch"])
        # Test adding value to list
        button_groups = arch.xpath("//button[@name='action_show_groups']")[0]
        self.assertEqual(button_groups.get("state"), "new")
        # Test adding more than one value to list
        button_access = arch.xpath("//button[@name='action_show_accesses']")[0]
        self.assertEqual(button_access.get("state"), "new,active")
        # Test removing values from list
        button_rules = arch.xpath("//button[@name='action_show_rules']")[0]
        self.assertEqual(button_rules.get("state"), "")

    def test_python_dict_inheritance_attrs_missing_key(self):
        """We should get an error if we try to update a dict without specifing a key"""
        inherit_id = self.env.ref("base.view_partner_form").id
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
            self.ViewModel.inheritance_handler_attributes_python_dict(
                source, specs, inherit_id
            )

    def test_python_dict_inheritance_error_if_not_a_dict(self):
        """We should get an error if we try to update a non-dict attribute"""
        inherit_id = self.env.ref("base.view_partner_form").id
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
            self.ViewModel.inheritance_handler_attributes_python_dict(
                source, specs, inherit_id
            )
