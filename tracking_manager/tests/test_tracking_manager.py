# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestTrackingManager(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Using the model res.partner for testing :
        #     - street field as regular field
        #     - parent_name as related field
        #     - category_id as many2many field
        #     - bank_ids as one2many field with acc_number field to test
        #     changes.

        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.partner_1.bank_ids = [(6, 0, cls.env.ref("base.bank_partner_demo").ids)]
        cls.partner_model = cls.env["ir.model"].search(
            [("model", "=", cls.partner_1._name)], limit=1
        )
        cls.bank_partner_2 = cls.env["res.partner.bank"].create(
            {
                "acc_number": "1234567890",
                "partner_id": cls.partner_1.id,
            }
        )

    def test_1_ir_model_config(self):
        self.partner_model.apply_custom_tracking = True
        # custom_tracking_field_ids
        self.assertEqual(
            len(self.partner_model.field_id),
            len(self.partner_model.custom_tracking_field_ids),
        )
        # o2m_model_ids
        self.assertEqual(
            len(self.partner_model.o2m_model_ids),
            len(self.partner_model.field_id.filtered(lambda x: x.ttype == "one2many")),
        )

    def test_2_tracking_model_field_config(self):
        self.partner_2 = self.env.ref("base.res_partner_2")
        self.partner_1_w_parent = self.env.ref("base.res_partner_address_1")
        self.partner_model.apply_custom_tracking = True
        # Readonly, related are not tracked
        parent_name = self.partner_model.custom_tracking_field_ids.filtered(
            lambda x: x.name == "parent_name"
        )
        self.assertFalse(parent_name.custom_tracking)
        # Other fields are tracked
        street = self.partner_model.custom_tracking_field_ids.filtered(
            lambda x: x.name == "street"
        )
        self.assertTrue(street.custom_tracking)

    def test_3_m2m_add_line(self):
        initial_msg = self.partner_1.message_ids
        self.partner_1.category_id = [
            (4, self.env.ref("base.res_partner_category_3").id)
        ]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg), len(after_msg))

        self.partner_model.apply_custom_tracking = True
        self.partner_1.category_id = [
            (4, self.env.ref("base.res_partner_category_8").id)
        ]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertTrue("New" in after_msg[0].body)

    def test_4_m2m_delete_line(self):
        initial_msg = self.partner_1.message_ids
        self.partner_1.category_id = [(3, self.partner_1.category_id[0].id)]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg), len(after_msg))

        self.partner_model.apply_custom_tracking = True
        self.partner_1.category_id = [(3, self.partner_1.category_id[0].id)]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertTrue("Delete" in after_msg[0].body)

    def test_5_m2m_multi_line(self):
        initial_msg = self.partner_1.message_ids
        self.partner_model.apply_custom_tracking = True
        self.partner_1.category_id = [
            (3, self.partner_1.category_id[0].id),
            (4, self.env.ref("base.res_partner_category_8").id),
            (4, self.env.ref("base.res_partner_category_11").id),
        ]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertEqual(after_msg[0].body.count("New"), 2)
        self.assertEqual(after_msg[0].body.count("Delete"), 1)

    def test_6_o2m_add(self):
        initial_msg = self.partner_1.message_ids
        self.partner_model.apply_custom_tracking = True
        self.partner_1.bank_ids = [(4, self.bank_partner_2.id)]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertTrue("New" in after_msg[0].body)

    def test_7_o2m_delete(self):
        self.partner_model.apply_custom_tracking = True
        initial_msg = self.partner_1.message_ids
        self.partner_1.write({"bank_ids": [(3, self.partner_1.bank_ids[0].id)]})
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertTrue("Delete" in after_msg[0].body)

    def test_8_o2m_change_in_line(self):
        self.partner_1.bank_ids = [(6, 0, self.bank_partner_2.id)]
        initial_msg = self.partner_1.message_ids
        self.partner_model.apply_custom_tracking = True
        self.partner_1.write(
            {
                "bank_ids": [(1, self.partner_1.bank_ids.id, {"acc_number": "123"})],
            }
        )
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertTrue("Change" in after_msg[0].body)
        # Restrict the tracking of acc_number
        bank_model = self.env["ir.model"].search(
            [("model", "=", self.bank_partner_2._name)], limit=1
        )
        bank_model.apply_custom_tracking = True
        acc_number = bank_model.custom_tracking_field_ids.filtered(
            lambda x: x.name == "acc_number"
        )
        acc_number.custom_tracking = False
        self.partner_1.write(
            {
                "bank_ids": [(1, self.partner_1.bank_ids.id, {"acc_number": "456"})],
            }
        )
        after_msg_2 = self.partner_1.message_ids
        self.assertEqual(len(after_msg), len(after_msg_2))

    def test_9_o2m_multi_line(self):
        initial_msg = self.partner_1.message_ids
        self.partner_model.apply_custom_tracking = True
        self.partner_1.bank_ids = [
            (3, self.partner_1.bank_ids[0].id),
            (4, self.bank_partner_2.id),
        ]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertEqual(after_msg[0].body.count("New"), 1)
        self.assertEqual(after_msg[0].body.count("Delete"), 1)
