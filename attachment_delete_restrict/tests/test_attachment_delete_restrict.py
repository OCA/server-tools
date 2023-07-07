# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


class AbstractCase:
    def test_restrict_none(self):
        self._set_restrict_mode("none")
        self.attachment.with_user(self.user).unlink()

    def test_restrict_custom_user(self):
        self._set_restrict_mode("custom")
        with self.assertRaises(ValidationError):
            self.attachment.with_user(self.user).unlink()
        self._allow_user()
        self.attachment.with_user(self.user).unlink()

    def test_restrict_custom_group(self):
        self._set_restrict_mode("custom")
        with self.assertRaises(ValidationError):
            self.attachment.with_user(self.user).unlink()
        self._allow_group()
        self.attachment.with_user(self.user).unlink()

    def test_restrict_owner(self):
        self._set_restrict_mode("owner")
        with self.assertRaises(ValidationError):
            self.attachment.with_user(self.user).unlink()
        self.attachment.with_user(self.user_owner).unlink()

    def test_restrict_owner_admin(self):
        self._set_restrict_mode("owner")
        self.attachment.with_user(self.user_admin).unlink()

    def test_restrict_owner_and_custom_user_forbiden(self):
        self._set_restrict_mode("owner_custom")
        with self.assertRaises(ValidationError):
            self.attachment.with_user(self.user).unlink()

    def test_restrict_owner_and_custom_user_owner(self):
        self._set_restrict_mode("owner_custom")
        self.attachment.with_user(self.user_owner).unlink()

    def test_restrict_owner_and_custom_user_admin(self):
        self._set_restrict_mode("owner_custom")
        self.attachment.with_user(self.user_admin).unlink()

    def test_restrict_owner_and_custom_user(self):
        self._set_restrict_mode("owner_custom")
        with self.assertRaises(ValidationError):
            self.attachment.with_user(self.user).unlink()
        self._allow_user()
        self.attachment.with_user(self.user).unlink()

    def test_restrict_owner_and_custom_user_group(self):
        self._set_restrict_mode("owner_custom")
        with self.assertRaises(ValidationError):
            self.attachment.with_user(self.user).unlink()
        self._allow_group()
        self.attachment.with_user(self.user).unlink()


@tagged("post_install", "-at_install")
class TestAttachmentDeleteAbstract(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.param = cls.env["ir.config_parameter"]
        cls.param.set_param(
            "attachment_delete_restrict.global_restrict_delete_attachment", "none"
        )
        cls.partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")])
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner_1"})
        cls.group = cls.env.ref("base.group_user")
        cls.user_owner = cls.env["res.users"].create(
            {
                "name": "test owner user",
                "login": "test-owner@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        (
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("base.group_partner_manager").id,
                        ),
                    )
                ],
            }
        )
        cls.user = cls.env["res.users"].create(
            {
                "name": "test user",
                "login": "test2@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        (
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("base.group_partner_manager").id,
                        ),
                    )
                ],
            }
        )
        cls.user_admin = cls.env["res.users"].create(
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
                            cls.env.ref("base.group_partner_manager").id,
                        ),
                    )
                ],
            }
        )
        cls.attachment = (
            cls.env["ir.attachment"]
            .with_user(cls.user_owner)
            .create(
                {
                    "name": "test attachment 2",
                    "type": "binary",
                    "res_model": "res.partner",
                    "res_id": cls.partner_1.id,
                }
            )
        )

    def _set_restrict_mode(self, restrict_mode):
        raise NotImplementedError

    def _allow_user(self):
        raise NotImplementedError

    def _allow_group(self):
        raise NotImplementedError


class TestAttachmentDeleteGlobal(TestAttachmentDeleteAbstract, AbstractCase):
    def _set_restrict_mode(self, restrict_mode):
        self.param.set_param(
            "attachment_delete_restrict.global_restrict_delete_attachment",
            restrict_mode,
        )

    def _allow_user(self):
        self.param.set_param(
            "attachment_delete_restrict.global_delete_attachment_user_ids",
            self.user.ids,
        )

    def _allow_group(self):
        self.param.set_param(
            "attachment_delete_restrict.global_delete_attachment_group_ids",
            self.group.ids,
        )


class TestAttachmentDeleteModel(TestAttachmentDeleteAbstract, AbstractCase):
    def _set_restrict_mode(self, restrict_mode):
        self.partner_model.write({"restrict_delete_attachment": restrict_mode})

    def _allow_user(self):
        self.partner_model.write({"delete_attachment_user_ids": [(4, self.user.id)]})

    def _allow_group(self):
        self.partner_model.write({"delete_attachment_group_ids": [(4, self.group.id)]})
