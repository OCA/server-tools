# Copyright 2021-2024 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import AccessError, UserError
from odoo.fields import Command
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestBaseModelRestrictUpdate(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_partner = cls.env["ir.model"].search([("model", "=", "res.partner")])
        cls.group_partner_update = cls.env["res.groups"].create(
            {"name": "Partner Update Group"}
        )
        cls.test_user = cls.env["res.users"].create({"name": "test", "login": "test"})
        cls.partner_model_with_test_user = cls.env["res.partner"].with_user(
            cls.test_user.id
        )
        cls.test_partner_with_test_user = (
            cls.env["res.partner"].with_user(cls.test_user.id).create({"name": "foo"})
        )

    def test_no_restriction(self):
        self.partner_model_with_test_user.create({"name": "bar"})
        self.test_partner_with_test_user.write({"name": "baz"})
        self.test_partner_with_test_user.unlink()

    def test_with_model_restriction(self):
        self.model_partner.restrict_update = True
        with self.assertRaises(AccessError):
            self.partner_model_with_test_user.create({"name": "bar"})
        with self.assertRaises(AccessError):
            self.test_partner_with_test_user.write({"name": "baz"})
        with self.assertRaises(AccessError):
            self.test_partner_with_test_user.unlink()
        self.model_partner.update_allowed_group_ids = self.group_partner_update
        with self.assertRaises(AccessError):
            self.partner_model_with_test_user.create({"name": "bar"})
        with self.assertRaises(AccessError):
            self.test_partner_with_test_user.write({"name": "baz"})
        with self.assertRaises(AccessError):
            self.test_partner_with_test_user.unlink()
        self.test_user.groups_id = [Command.link(self.group_partner_update.id)]
        self.partner_model_with_test_user.create({"name": "bar"})
        self.test_partner_with_test_user.write({"name": "baz"})
        self.test_partner_with_test_user.unlink()

    def test_with_user_readonly(self):
        self.test_user.is_readonly_user = True
        with self.assertRaises(AccessError):
            self.partner_model_with_test_user.create({"name": "bar"})
        with self.assertRaises(AccessError):
            self.test_partner_with_test_user.write({"name": "baz"})
        with self.assertRaises(AccessError):
            self.test_partner_with_test_user.unlink()
        # To confirm that is_readonly_user prevails
        self.model_partner.restrict_update = True
        self.model_partner.update_allowed_group_ids = self.group_partner_update
        self.test_user.groups_id = [Command.link(self.group_partner_update.id)]
        with self.assertRaises(AccessError):
            self.partner_model_with_test_user.create({"name": "bar"})
        with self.assertRaises(AccessError):
            self.test_partner_with_test_user.write({"name": "baz"})
        with self.assertRaises(AccessError):
            self.test_partner_with_test_user.unlink()
        self.test_user.is_readonly_user = False
        self.partner_model_with_test_user.create({"name": "bar"})
        self.test_partner_with_test_user.write({"name": "baz"})
        self.test_user.is_readonly_user = True
        with self.assertRaises(AccessError):
            self.test_partner_with_test_user.write({"name": "qux"})
        with self.assertRaises(AccessError):
            self.test_partner_with_test_user.unlink()
        self.env["ir.config_parameter"].sudo().set_param(
            "base_model_restrict_update.excluded_models_from_readonly", "res.partner"
        )
        self.test_partner_with_test_user.write({"name": "qux"})
        self.test_partner_with_test_user.unlink()

    def test_set_user_readonly(self):
        group_system_id = self.env.ref("base.group_system").id
        self.test_user.groups_id = [Command.link(group_system_id)]
        with self.assertRaises(UserError):
            self.test_user.is_readonly_user = True
        self.test_user.groups_id = [Command.unlink(group_system_id)]
        self.test_user.is_readonly_user = True
        with self.assertRaises(UserError):
            self.test_user.groups_id = [Command.link(group_system_id)]
