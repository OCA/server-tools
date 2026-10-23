# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from importlib import import_module

from odoo.exceptions import AccessError
from odoo.fields import Domain
from odoo.orm.model_classes import add_to_registry
from odoo.tests.common import TransactionCase


class TestBaseMixinRestrictFieldAccess(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Save original base classes so we can restore after tests
        cls.original_partner_base_classes = cls.registry["res.partner"]._base_classes__

        RestrictFieldAccessPartner = import_module(
            ".test_models",
            package=__package__,
        ).RestrictFieldAccessPartner

        add_to_registry(cls.registry, RestrictFieldAccessPartner)
        cls.registry._setup_models__(cls.env.cr, ["res.partner"])
        cls.registry.init_models(
            cls.env.cr,
            ["res.partner"],
            {"models_to_check": True},
        )
        cls.addClassCleanup(cls.restore_partner)

        # Create a non-privileged user for testing
        cls.demo_user = cls.env["res.users"].create(
            {
                "name": "Test Demo User",
                "login": "test_restrict_field_demo",
                "group_ids": [
                    (6, 0, [cls.env.ref("base.group_user").id]),
                ],
            }
        )

    @classmethod
    def restore_partner(cls):
        cls.registry["res.partner"]._base_classes__ = cls.original_partner_base_classes

    def test_restrict_field_access_false_when_below_limit(self):
        """restrict_field_access should be False when test_credit_limit < 42"""
        partner_model = self.env["res.partner"].with_user(self.demo_user)
        partner = partner_model.create({"name": "testpartner"})
        self.assertFalse(partner.restrict_field_access)

    def test_restrict_field_access_true_when_at_limit(self):
        """restrict_field_access should be True when test_credit_limit >= 42"""
        partner_model = self.env["res.partner"].with_user(self.demo_user)
        partner = partner_model.create({"name": "testpartner"})
        partner.sudo().write({"test_credit_limit": 42})
        partner.invalidate_recordset()
        self.assertTrue(partner.restrict_field_access)

    def test_read_restricted_field_raises_access_error(self):
        """Reading a restricted field should raise AccessError"""
        partner_model = self.env["res.partner"].with_user(self.demo_user)
        partner = partner_model.create({"name": "testpartner"})
        partner.sudo().write({"test_credit_limit": 42})
        partner.invalidate_recordset()
        with self.assertRaises(AccessError):
            partner.read(["test_credit_limit"])

    def test_read_restricted_field_accessible_with_sudo(self):
        """Sudo should bypass field restrictions"""
        partner_model = self.env["res.partner"].with_user(self.demo_user)
        partner = partner_model.create({"name": "testpartner"})
        partner.sudo().write({"test_credit_limit": 42})
        partner.invalidate_recordset()
        self.assertEqual(partner.sudo().test_credit_limit, 42)

    def test_search_unrestricted_field_includes_partner(self):
        """Searching without restricted fields should yield the partner"""
        partner_model = self.env["res.partner"].with_user(self.demo_user)
        partner = partner_model.create({"name": "testpartner"})
        partner.sudo().write({"test_credit_limit": 42})
        partner.invalidate_recordset()
        self.assertIn(partner, partner_model.search([]))

    def test_search_restricted_field_excludes_partner(self):
        """Searching on a restricted field should not yield the partner"""
        partner_model = self.env["res.partner"].with_user(self.demo_user)
        partner = partner_model.create({"name": "testpartner"})
        partner.sudo().write({"test_credit_limit": 42})
        partner.invalidate_recordset()
        self.assertNotIn(
            partner,
            partner_model.search([("test_credit_limit", "=", 42)]),
        )

    def test_search_restricted_domain_object_excludes_partner(self):
        """Searching with a composite Domain should not crash or yield partner."""
        partner_model = self.env["res.partner"].with_user(self.demo_user)
        partner = partner_model.create({"name": "testpartner"})
        partner.sudo().write({"test_credit_limit": 42})
        partner.invalidate_recordset()
        domain = Domain.AND(
            [[("test_credit_limit", "=", 42)], [("name", "=", "testpartner")]]
        )
        self.assertNotIn(partner, partner_model.search(domain))

    def test_copy_restricted_fields_copied_but_inaccessible(self):
        """Copying should copy restricted fields but keep them inaccessible"""
        partner_model = self.env["res.partner"].with_user(self.demo_user)
        partner = partner_model.create({"name": "testpartner"})
        partner.sudo().write({"test_credit_limit": 42})
        partner.invalidate_recordset()
        new_partner = partner.copy()
        with self.assertRaises(AccessError):
            new_partner.read(["test_credit_limit"])
        self.assertEqual(new_partner.sudo().test_credit_limit, 42)

    def test_get_view_injects_restrict_field_access(self):
        """get_view should inject restrict_field_access into the arch"""
        partner_model = self.env["res.partner"].with_user(self.demo_user)
        partner = partner_model.create({"name": "testpartner"})
        view = partner.get_view(view_type="form")
        self.assertIn("restrict_field_access", view["arch"])

    def test_export_restricted_field_returns_null(self):
        """Exporting a restricted field should return null value"""
        partner_model = self.env["res.partner"].with_user(self.demo_user)
        partner = partner_model.create({"name": "testpartner"})
        partner.sudo().write({"test_credit_limit": 42})
        partner.invalidate_recordset()
        export = partner._export_rows([["id"], ["test_credit_limit"]])
        self.assertFalse(export[0][1])

    def test_export_accessible_field_returns_value(self):
        """Exporting an accessible field should return the actual value"""
        partner_model = self.env["res.partner"].with_user(self.demo_user)
        partner = partner_model.create({"name": "testpartner"})
        partner.sudo().write({"test_credit_limit": 41})
        partner.invalidate_recordset()
        export = partner._export_rows([["id"], ["test_credit_limit"]])
        self.assertEqual(export[0][1], 41.0)
