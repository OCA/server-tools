# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestAttachmentDeleteRestrict(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.param = cls.env["ir.config_parameter"].sudo()
        cls.param.set_param(
            "attachment_delete_restrict.global_restrict_delete_attachment", "none"
        )
        cls.partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")])
        cls.test_group = cls.env["res.groups"].create({"name": "test group"})
        cls.test_user = cls.env["res.users"].create(
            {
                "name": "test user",
                "login": "test@example.com",
                "groups_id": [(6, 0, cls.env.ref("base.group_user").ids)],
            }
        )
        cls.test_user2 = cls.env["res.users"].create(
            {
                "name": "test user2",
                "login": "test2@example.com",
                "groups_id": [(6, 0, cls.env.ref("base.group_user").ids)],
            }
        )
        cls.test_admin = cls.env["res.users"].create(
            {
                "name": "User admin",
                "login": "admin@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        (
                            cls.env.ref("base.group_system").id,
                            cls.env.ref("base.group_user").id,
                        ),
                    )
                ],
            }
        )
        cls.test_attachment = cls.env["ir.attachment"].create(
            {"name": "test attachment", "type": "binary", "res_model": "res.partner"}
        )
        cls.test_attachment_2 = (
            cls.env["ir.attachment"]
            .with_user(cls.test_user)
            .create(
                {
                    "name": "test attachment 2",
                    "type": "binary",
                    "res_model": "res.partner",
                }
            )
        )

    def test_01_delete_attachment_unrestricted(self):
        self.test_attachment.with_user(self.test_user).unlink()

    def test_01_bis_delete_attachment_unrestricted(self):
        self.partner_model.write({"restrict_delete_attachment": "none"})
        self.test_attachment.with_user(self.test_user2).unlink()

    def test_02_custom_delete_attachment_restricted_user_permitted(self):
        self.partner_model.write({"restrict_delete_attachment": "custom"})
        with self.assertRaises(ValidationError):
            self.test_attachment.with_user(self.test_user).unlink()
        self.partner_model.write(
            {"delete_attachment_user_ids": [(4, self.test_user.id)]}
        )
        self.test_attachment.with_user(self.test_user).unlink()

    def test_03_custom_delete_attachment_restricted_group_permitted(self):
        self.partner_model.write({"restrict_delete_attachment": "custom"})
        with self.assertRaises(ValidationError):
            self.test_attachment.with_user(self.test_user).unlink()
        self.partner_model.write(
            {"delete_attachment_group_ids": [(4, self.test_group.id)]}
        )
        with self.assertRaises(ValidationError):
            self.test_attachment.with_user(self.test_user).unlink()
        self.test_user.write({"groups_id": [(4, self.test_group.id)]})
        self.test_attachment.with_user(self.test_user).unlink()

    def test_04_restrict_owner_can_delete_attachment(self):
        self.partner_model.write({"restrict_delete_attachment": "restrict"})
        test_attachment_2 = (
            self.env["ir.attachment"]
            .with_user(self.test_user)
            .create(
                {
                    "name": "test attachment 2",
                    "type": "binary",
                    "res_model": "res.partner",
                }
            )
        )
        with self.assertRaises(ValidationError):
            test_attachment_2.with_user(self.test_user2).unlink()
        test_attachment_2.with_user(self.test_user).unlink()

    def test_05_restrict_admin_can_delete_attachment(self):
        self.partner_model.write({"restrict_delete_attachment": "restrict"})
        self.test_attachment.with_user(self.test_admin).unlink()

    def test_06_global_restrict_restriction(self):
        self.param.set_param(
            "attachment_delete_restrict.global_restrict_delete_attachment", "restrict"
        )
        with self.assertRaises(ValidationError):
            self.test_attachment_2.with_user(self.test_user2).unlink()
        self.test_attachment_2.with_user(self.test_user).unlink()

    def test_07_global_custom_restriction_for_users(self):
        self.param.set_param(
            "attachment_delete_restrict.global_restrict_delete_attachment", "custom"
        )
        self.param.set_param(
            "attachment_delete_restrict.global_delete_attachment_user_ids",
            self.test_user2.ids,
        )
        with self.assertRaises(ValidationError):
            self.test_attachment.with_user(self.test_user).unlink()
        self.test_attachment.with_user(self.test_user2).unlink()

    def test_08_global_custom_restriction_for_groups(self):
        self.param.set_param(
            "attachment_delete_restrict.global_restrict_delete_attachment", "custom"
        )
        with self.assertRaises(ValidationError):
            self.test_attachment.with_user(self.test_user).unlink()
        self.param.set_param(
            "attachment_delete_restrict.global_delete_attachment_group_ids",
            self.test_group.ids,
        )
        with self.assertRaises(ValidationError):
            self.test_attachment.with_user(self.test_user).unlink()
        self.test_user.write({"groups_id": [(4, self.test_group.id)]})
        self.test_attachment.with_user(self.test_user).unlink()

    def test_09_global_none_restriction(self):
        global_restrict = self.param.get_param(
            "attachment_delete_restrict.global_restrict_delete_attachment"
        )
        self.assertEqual(global_restrict, "none")
        self.test_attachment.with_user(self.test_user).unlink()

    def test_10_restrict_and_custom_delete_user(self):
        self.partner_model.write({"restrict_delete_attachment": "restrict_custom"})
        with self.assertRaises(ValidationError):
            self.test_attachment.with_user(self.test_user2).unlink()
        self.partner_model.write(
            {"delete_attachment_user_ids": [(4, self.test_user2.id)]}
        )
        self.test_attachment.with_user(self.test_user2).unlink()

        self.test_attachment_2.with_user(self.test_admin).unlink()

    def test_11_restrict_and_custom_delete_group(self):
        self.param.set_param(
            "attachment_delete_restrict.global_restrict_delete_attachment",
            "restrict_custom",
        )
        with self.assertRaises(ValidationError):
            self.test_attachment.with_user(self.test_user).unlink()
        self.test_user.write({"groups_id": [(4, self.test_group.id)]})
        self.param.set_param(
            "attachment_delete_restrict.global_delete_attachment_group_ids",
            self.test_group.ids,
        )
        self.test_attachment.with_user(self.test_user).unlink()
        self.test_attachment_2.with_user(self.test_admin).unlink()

    def test_12_default_model_restriction(self):
        self.param.set_param(
            "attachment_delete_restrict.global_restrict_delete_attachment", "custom"
        )
        self.param.set_param(
            "attachment_delete_restrict.global_delete_attachment_group_ids",
            self.test_group.ids,
        )
        self.partner_model.write({"restrict_delete_attachment": "default"})
        with self.assertRaises(ValidationError):
            self.test_attachment.with_user(self.test_user).unlink()

        self.test_user.write({"groups_id": [(4, self.test_group.id)]})
        self.test_attachment.with_user(self.test_user).unlink()
