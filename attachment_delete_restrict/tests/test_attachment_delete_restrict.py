# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestAttachmentDeleteRestrict(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")])
        cls.test_group = cls.env["res.groups"].create({"name": "test group"})
        cls.test_user = cls.env["res.users"].create(
            {"name": "test user", "login": "test@example.com"}
        )
        cls.test_attachment = cls.env["ir.attachment"].create(
            {"name": "test attachment", "type": "binary", "res_model": "res.partner"}
        )

    def test_01_delete_attachment_unrestricted(self):
        self.test_attachment.sudo(self.test_user).unlink()

    def test_02_delete_attachment_restricted_user_permitted(self):
        self.partner_model.write({"restrict_delete_attachment": True})
        with self.assertRaises(ValidationError):
            self.test_attachment.sudo(self.test_user).unlink()
        self.partner_model.write(
            {"delete_attachment_user_ids": [(4, self.test_user.id)]}
        )
        self.test_attachment.sudo(self.test_user).unlink()

    def test_03_delete_attachment_restricted_group_permitted(self):
        self.partner_model.write({"restrict_delete_attachment": True})
        with self.assertRaises(ValidationError):
            self.test_attachment.sudo(self.test_user).unlink()
        self.partner_model.write(
            {"delete_attachment_group_ids": [(4, self.test_group.id)]}
        )
        with self.assertRaises(ValidationError):
            self.test_attachment.sudo(self.test_user).unlink()
        self.test_user.write({"groups_id": [(4, self.test_group.id)]})
        self.test_attachment.sudo(self.test_user).unlink()
