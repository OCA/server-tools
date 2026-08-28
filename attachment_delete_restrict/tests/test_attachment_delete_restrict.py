# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, Command
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

    def test_restrict_custom_user_with_superuser(self):
        self._set_restrict_mode("custom")
        self.attachment.with_user(SUPERUSER_ID).unlink()

    def test_restrict_custom_group(self):
        self._set_restrict_mode("custom")
        with self.assertRaises(ValidationError):
            self.attachment.with_user(self.user).unlink()
        self._allow_group()
        self.attachment.with_user(self.user).unlink()

    def test_restrict_custom_implied_group(self):
        # Regression: the authorized group may be held by the user only
        # through group implication. Membership must be resolved with
        # all_user_ids (implication-aware), not user_ids (explicit members
        # only), otherwise such a user is wrongly denied deletion.
        self._set_restrict_mode("custom")
        child_group = self.env["res.groups"].create({"name": "Delete child group"})
        self.env["res.groups"].create(
            {
                "name": "Delete parent group",
                "implied_ids": [Command.link(child_group.id)],
                "user_ids": [Command.link(self.user.id)],
            }
        )
        # The user belongs to child_group only via implication.
        self.assertNotIn(self.user, child_group.user_ids)
        self.assertIn(self.user, child_group.all_user_ids)
        with self.assertRaises(ValidationError):
            self.attachment.with_user(self.user).unlink()
        self._allow_groups(child_group)
        self.attachment.with_user(self.user).unlink()

    def test_restrict_owner(self):
        self._set_restrict_mode("owner")
        with self.assertRaises(ValidationError):
            self.attachment.with_user(self.user).unlink()
        self.attachment.with_user(self.user_owner).unlink()

    def test_restrict_owner_admin(self):
        self._set_restrict_mode("owner")
        self.attachment.with_user(self.user_admin).unlink()

    def test_restrict_owner_and_custom_user_forbidden(self):
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
    allow_inherited_tests_method = True

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
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("base.group_partner_manager").id,
                        ]
                    )
                ],
            }
        )
        cls.user = cls.env["res.users"].create(
            {
                "name": "test user",
                "login": "test2@example.com",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("base.group_partner_manager").id,
                        ]
                    )
                ],
            }
        )
        cls.user_admin = cls.env["res.users"].create(
            {
                "name": "User admin",
                "login": "admin@example.com",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("base.group_system").id,
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("base.group_partner_manager").id,
                        ]
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

    def test_unlink_orphan_res_model(self):
        # An attachment whose res_model is not a registered model (e.g. left
        # over from an uninstalled module) must not crash unlink; it falls
        # back to the global configuration.
        self.param.set_param(
            "attachment_delete_restrict.global_restrict_delete_attachment", "owner"
        )
        attachment = (
            self.env["ir.attachment"]
            .with_user(self.user_owner)
            .create(
                {
                    "name": "orphan attachment",
                    "type": "binary",
                    "res_model": "non.existent.model",
                    "res_id": 1,
                }
            )
        )
        with self.assertRaises(ValidationError):
            attachment.with_user(self.user).unlink()
        attachment.with_user(self.user_owner).unlink()

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
        self._allow_groups(self.group)

    def _allow_groups(self, groups):
        self.param.set_param(
            "attachment_delete_restrict.global_delete_attachment_group_ids",
            groups.ids,
        )


class TestAttachmentDeleteModel(TestAttachmentDeleteAbstract, AbstractCase):
    def _set_restrict_mode(self, restrict_mode):
        self.partner_model.write({"restrict_delete_attachment": restrict_mode})

    def _allow_user(self):
        self.partner_model.write({"delete_attachment_user_ids": [(4, self.user.id)]})

    def _allow_group(self):
        self._allow_groups(self.group)

    def _allow_groups(self, groups):
        self.partner_model.write(
            {"delete_attachment_group_ids": [Command.link(g) for g in groups.ids]}
        )
