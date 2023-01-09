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

    def _active_tracking(self, fields_list):
        self.partner_model.active_custom_tracking = True
        for field in self._get_fields(fields_list):
            field.custom_tracking = True

    def _get_fields(self, fields_list):
        return self.env["ir.model.fields"].search(
            [
                ("model_id.model", "=", "res.partner"),
                ("name", "in", fields_list),
            ]
        )

    def test_not_tracked(self):
        self.partner_model.active_custom_tracking = True
        field = self._get_fields(["category_id"])[0]
        self.assertFalse(field.native_tracking)
        self.assertFalse(field.custom_tracking)

    def test_native_tracked(self):
        self.partner_model.active_custom_tracking = True
        field = self._get_fields(["email"])[0]
        self.assertTrue(field.native_tracking)
        self.assertTrue(field.custom_tracking)

    def test_update_tracked(self):
        self.partner_model.active_custom_tracking = True
        field = self._get_fields(["category_id"])[0]
        self.assertFalse(field.native_tracking)
        self.partner_model.automatic_custom_tracking = True
        self.partner_model.update_custom_tracking()
        self.assertTrue(field.custom_tracking)

    def test_m2m_add_line(self):
        initial_msg = self.partner_1.message_ids
        self.partner_1.category_id = [
            (4, self.env.ref("base.res_partner_category_3").id)
        ]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg), len(after_msg))

        self._active_tracking(["category_id"])
        self.partner_1.category_id = [
            (4, self.env.ref("base.res_partner_category_8").id)
        ]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertTrue("New" in after_msg[0].body)

    def test_m2m_delete_line(self):
        initial_msg = self.partner_1.message_ids
        self.partner_1.category_id = [(3, self.partner_1.category_id[0].id)]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg), len(after_msg))

        self._active_tracking(["category_id"])
        self.partner_1.category_id = [(3, self.partner_1.category_id[0].id)]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertTrue("Delete" in after_msg[0].body)

    def test_m2m_multi_line(self):
        initial_msg = self.partner_1.message_ids
        self._active_tracking(["category_id"])
        self.partner_1.category_id = [
            (3, self.partner_1.category_id[0].id),
            (4, self.env.ref("base.res_partner_category_8").id),
            (4, self.env.ref("base.res_partner_category_11").id),
        ]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertEqual(after_msg[0].body.count("New"), 2)
        self.assertEqual(after_msg[0].body.count("Delete"), 1)

    def test_o2m_add(self):
        initial_msg = self.partner_1.message_ids
        self._active_tracking(["bank_ids"])
        self.partner_1.bank_ids = [(4, self.bank_partner_2.id)]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertTrue("New" in after_msg[0].body)

    def test_o2m_delete(self):
        self._active_tracking(["bank_ids"])
        initial_msg = self.partner_1.message_ids
        self.partner_1.write({"bank_ids": [(3, self.partner_1.bank_ids[0].id)]})
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertTrue("Delete" in after_msg[0].body)

    def test_o2m_change_in_line(self):
        self.partner_1.bank_ids = [(6, 0, self.bank_partner_2.id)]
        initial_msg = self.partner_1.message_ids
        self._active_tracking(["bank_ids"])
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
        bank_model.active_custom_tracking = True
        acc_number = bank_model.field_id.filtered(lambda x: x.name == "acc_number")
        acc_number.custom_tracking = False
        self.partner_1.write(
            {
                "bank_ids": [(1, self.partner_1.bank_ids.id, {"acc_number": "456"})],
            }
        )
        after_msg_2 = self.partner_1.message_ids
        self.assertEqual(len(after_msg), len(after_msg_2))

    def test_o2m_multi_line(self):
        initial_msg = self.partner_1.message_ids
        self._active_tracking(["bank_ids"])
        self.partner_1.bank_ids = [
            (3, self.partner_1.bank_ids[0].id),
            (4, self.bank_partner_2.id),
        ]
        after_msg = self.partner_1.message_ids
        self.assertEqual(len(initial_msg) + 1, len(after_msg))
        self.assertEqual(after_msg[0].body.count("New"), 1)
        self.assertEqual(after_msg[0].body.count("Delete"), 1)
