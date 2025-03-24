# Copyright 2025 glueckkanja AG (<https://www.glueckkanja.com>) - Christopher Rogos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMailTrack(TransactionCase):
    def setUp(self):
        super().setUp()

        self.Field = self.env["ir.model.fields"]
        self.field_mobile = self.Field.search(
            [("model", "=", "res.partner"), ("name", "=", "mobile")], limit=1
        )
        self.field_mobile.write({"tracking_domain": "[('is_company', '=', True)]"})

    def test_mail_track(self):
        # arrange
        company = self.env.ref("base.res_partner_12")
        tracked_fields = {"mobile": {"string": "Mobile", "type": "char"}}
        initial_values = {"mobile": "1234"}

        # act
        changes, tracking_value_ids = company._mail_track(
            tracked_fields, initial_values
        )

        # assert
        # Check if changes and tracking_value_ids are returned correctly
        self.assertEqual(len(changes), 1)
        self.assertEqual(len(tracking_value_ids), 1)

        # Check if the field is tracked correctly
        tracking_value = tracking_value_ids[0][2]
        self.assertEqual(tracking_value["field_id"], self.field_mobile.id)

    def test_mail_track_with_non_matching_domain(self):
        # arrange
        person = self.env.ref("base.partner_admin")

        tracked_fields = {"mobile": {"string": "Mobile", "type": "char"}}
        initial_values = {"mobile": "1234"}

        # act
        changes, tracking_value_ids = person._mail_track(tracked_fields, initial_values)

        # assert
        # Check if changes and tracking_value_ids are empty when domain does not match
        self.assertEqual(len(changes), 0)
        self.assertEqual(len(tracking_value_ids), 0)
