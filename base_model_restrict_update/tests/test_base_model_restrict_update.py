# Copyright 2021 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import AccessError
from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestBaseModelRestrictUpdate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")])[
            0
        ]
        cls.partner_model.restrict_update = True
        cls.test_partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.restrict_test_user = cls.env["res.users"].create(
            {
                "name": "Resticted user",
                "login": "resticted@example.com",
                "unrestrict_model_update": False,
            }
        )
        cls.permit_test_user = cls.env["res.users"].create(
            {
                "name": "Permit user",
                "login": "permit@example.com",
                "email": "permit@example.com",
                "unrestrict_model_update": True,
            }
        )

    def test_01_create_partner(self):
        with self.assertRaises(AccessError):
            self.env["res.partner"].with_user(self.restrict_test_user.id).create(
                {"name": "Test Partner"}
            )
        self.env["res.partner"].with_user(self.permit_test_user.id).create(
            {"name": "Test Partner"}
        )

    def test_02_update_partner(self):
        with self.assertRaises(AccessError):
            self.test_partner.with_user(self.restrict_test_user.id).update(
                {"name": "Test Partner 2"}
            )
        self.test_partner.with_user(self.permit_test_user.id).update(
            {"name": "Test Partner 2"}
        )

    def test_03_unlink_partner(self):
        test_partner = self.test_partner.sudo().copy()
        with self.assertRaises(AccessError):
            test_partner.with_user(self.restrict_test_user.id).unlink()
        test_partner.with_user(self.permit_test_user.id).unlink()

    def test_04_readonly_user_update_partner(self):
        self.permit_test_user.write({"is_readonly_user": True})
        with self.assertRaises(AccessError):
            self.test_partner.with_user(self.permit_test_user.id).update(
                {"name": "Test Partner 2"}
            )

        self.partner_model.restrict_update = False
        with self.assertRaises(AccessError):
            self.test_partner.sudo(self.permit_test_user.id).update(
                {"name": "Test Partner 2"}
            )

        self.partner_model.skip_check_for_readonly_users = True
        self.test_partner.sudo(self.permit_test_user.id).update(
            {"name": "Test Partner 2"}
        )
