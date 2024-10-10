# Copyright 2022 Akretion (https://www.akretion.com).
# Copyright 2024 Tecnativa - Víctor Martínez
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestTrackingManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_categ_1, cls.partner_categ_2, cls.partner_categ_3 = cls.env[
            "res.partner.category"
        ].create(
            [
                {"name": "FOO"},
                {"name": "BAR"},
                {"name": "TOOH"},
            ]
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Foo",
                "user_ids": [(0, 0, {"login": "007"})],
                "category_id": [(6, 0, [cls.partner_categ_1.id])],
            }
        )
        cls.partner_model = cls.env.ref("base.model_res_partner")
        cls._active_tracking(["user_ids", "category_id"])
        cls.flush_tracking()
        cls.partner.message_ids.unlink()

    @classmethod
    def _active_tracking(cls, fields_list):
        cls.partner_model.active_custom_tracking = True
        for field in cls._get_fields(fields_list):
            field.custom_tracking = True

    @classmethod
    def _get_fields(cls, fields_list):
        return cls.partner_model.field_id.filtered(lambda s: s.name in fields_list)

    def test_not_tracked(self):
        field = self._get_fields(["name"])[0]
        self.assertFalse(field.native_tracking)
        self.assertFalse(field.custom_tracking)

    def test_native_tracked(self):
        field = self._get_fields(["email"])[0]
        self.assertTrue(field.native_tracking)
        self.assertTrue(field.custom_tracking)

    def test_update_tracked(self):
        field = self._get_fields(["name"])[0]
        self.assertFalse(field.native_tracking)
        self.partner_model.automatic_custom_tracking = True
        self.partner_model.update_custom_tracking()
        self.assertTrue(field.custom_tracking)

    @classmethod
    def flush_tracking(cls):
        """Force the creation of tracking values."""
        cls.env["base"].flush_model()
        cls.env.cr.precommit.run()

    @property
    def messages(self):
        # Force the creation of tracking values
        self.flush_tracking()
        return self.partner.message_ids

    def test_m2m_add_line(self):
        self.partner.write(
            {
                "category_id": [
                    (
                        6,
                        0,
                        [
                            self.partner_categ_1.id,
                            self.partner_categ_2.id,
                        ],
                    )
                ]
            }
        )
        self.assertEqual(len(self.messages), 1)
        tracking = self.messages.tracking_value_ids
        self.assertEqual(len(tracking), 1)
        self.assertEqual(tracking.old_value_char, "FOO")
        self.assertEqual(tracking.new_value_char, "FOO, BAR")

    def test_m2m_delete_line(self):
        self.partner.write({"category_id": [(6, 0, [])]})
        self.assertEqual(len(self.messages), 1)
        tracking = self.messages.tracking_value_ids
        self.assertEqual(len(tracking), 1)
        self.assertEqual(tracking.old_value_char, "FOO")
        self.assertEqual(tracking.new_value_char, "")

    def test_m2m_multi_line(self):
        self.partner.write(
            {
                "category_id": [
                    (
                        6,
                        0,
                        [
                            self.partner_categ_2.id,
                            self.partner_categ_3.id,
                        ],
                    )
                ]
            }
        )
        self.assertEqual(len(self.messages), 1)
        tracking = self.messages.tracking_value_ids
        self.assertEqual(len(tracking), 1)
        self.assertEqual(tracking.old_value_char, "FOO")
        self.assertEqual(tracking.new_value_char, "BAR, TOOH")

    def test_o2m_create_indirectly(self):
        self.partner.write({"user_ids": [(0, 0, {"login": "1234567890"})]})
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages.body.count("New"), 1)

    @mute_logger("odoo.models.unlink")
    def test_o2m_unlink_indirectly(self):
        self.partner.write({"user_ids": [(2, self.partner.user_ids[0].id)]})
        self.assertEqual(len(self.messages), 1)
        self.assertIn("Delete", self.messages.body)

    def test_o2m_write_indirectly(self):
        self.partner.write(
            {
                "user_ids": [(1, self.partner.user_ids[0].id, {"login": "123"})],
            }
        )
        self.assertEqual(len(self.messages), 1)
        self.assertIn("Change", self.messages.body)

    def test_o2m_write_indirectly_on_not_tracked_fields(self):
        # Active custom tracking on res.users and remove tracking on login
        res_users_model = self.env["ir.model"].search([("model", "=", "res.users")])
        res_users_model.active_custom_tracking = True
        login_field = res_users_model.field_id.filtered(lambda x: x.name == "login")
        login_field.custom_tracking = False
        self.partner.write(
            {
                "user_ids": [(1, self.partner.user_ids[0].id, {"login": "123"})],
            }
        )
        self.assertEqual(len(self.messages), 0)

    @mute_logger("odoo.models.unlink")
    def test_o2m_create_and_unlink_indirectly(self):
        self.partner.write(
            {
                "user_ids": [
                    (2, self.partner.user_ids[0].id, 0),
                    (0, 0, {"login": "1234567890"}),
                ]
            }
        )
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages.body.count("New"), 1)
        self.assertEqual(self.messages.body.count("Delete"), 1)

    def test_o2m_update_m2m_indirectly(self):
        self.group_extra = self.env["res.groups"].create({"name": "Test group"})
        self.partner.write(
            {
                "user_ids": [
                    (
                        1,
                        self.partner.user_ids[0].id,
                        {
                            "groups_id": [
                                (
                                    6,
                                    0,
                                    [
                                        self.env.ref("base.group_user").id,
                                        self.group_extra.id,
                                    ],
                                )
                            ]
                        },
                    ),
                ]
            }
        )
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages.body.count("Changed"), 1)

    def test_o2m_update_m2o_indirectly(self):
        self.partner.write(
            {
                "user_ids": [
                    (
                        1,
                        self.partner.user_ids[0].id,
                        {
                            "action_id": self.env["ir.actions.actions"]
                            .create({"name": "test", "type": "ir.actions.act_window"})
                            .id
                        },
                    ),
                ]
            }
        )
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages.body.count("Changed"), 1)

    @mute_logger("odoo.models.unlink")
    def test_o2m_write_and_unlink_indirectly(self):
        # when editing a o2m in some special case
        # like the computed field amount_tax of purchase order line
        # some write can be done on a line before behind deleted
        # line._compute_amount() is called manually inside see link behind
        # https://github.com/odoo/odoo/blob/009f35f3d3659792ef18ac510a6ec323708becec/addons/purchase/models/purchase.py#L28 # noqa
        # So we are in a case that we do some change and them we delete them
        # in that case we should only have one message of deletation
        # and no error
        self.partner.write(
            {
                "user_ids": [(1, self.partner.user_ids[0].id, {"login": "123"})],
            }
        )
        self.partner.write(
            {
                "user_ids": [(2, self.partner.user_ids[0].id, 0)],
            }
        )
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages.body.count("Change"), 0)
        self.assertEqual(self.messages.body.count("Delete"), 1)

    def test_o2m_create_directly(self):
        self.env["res.users"].create(
            {
                "name": "1234567890",
                "login": "1234567890",
                "partner_id": self.partner.id,
            }
        )
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages.body.count("New"), 1)

    @mute_logger("odoo.models.unlink")
    def test_o2m_unlink_directly(self):
        self.partner.user_ids.unlink()
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages.body.count("Delete"), 1)

    def test_o2m_update_directly(self):
        self.partner.user_ids.write({"login": "0987654321"})
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages.body.count("Change :"), 1)

    @mute_logger("odoo.models.unlink")
    def test_o2m_write_and_unlink_directly(self):
        # see explanation of test_o2m_write_and_unlink_indirectly
        self.partner.user_ids.write({"login": "0987654321"})
        self.partner.user_ids.unlink()
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages.body.count("Change"), 0)
        self.assertEqual(self.messages.body.count("Delete"), 1)

    def test_o2m_update_record(self):
        self.env.ref("base.field_res_partner__child_ids").custom_tracking = True
        child = self.env["res.partner"].create(
            {"name": "Test child", "parent_id": self.partner.id}
        )
        child.write({"parent_id": False})
        self.assertEqual(len(self.messages), 1)
