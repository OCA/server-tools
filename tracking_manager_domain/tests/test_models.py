# Copyright 2025 glueckkanja AG (<https://www.glueckkanja.com>) - Christopher Rogos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import Command
from odoo.tests.common import TransactionCase


class TestMailTrack(TransactionCase):
    def setUp(self):
        super().setUp()

        self.Field = self.env["ir.model.fields"]
        self.field_phone = self.Field.search(
            [("model", "=", "res.partner"), ("name", "=", "phone")], limit=1
        )
        self.field_phone.write({"tracking_domain": "[('is_company', '=', True)]"})

    def test_mail_track(self):
        # arrange
        company = self.env.ref("base.main_partner")
        tracked_fields = {"phone": {"string": "Phone", "type": "char"}}
        initial_values = {"phone": "1234"}

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
        self.assertEqual(tracking_value["field_id"], self.field_phone.id)

    def test_mail_track_with_non_matching_domain(self):
        # arrange
        person = self.env.ref("base.partner_admin")

        tracked_fields = {"phone": {"string": "Phone", "type": "char"}}
        initial_values = {"phone": "1234"}

        # act
        changes, tracking_value_ids = person._mail_track(tracked_fields, initial_values)

        # assert
        # Check if changes and tracking_value_ids are empty when domain does not match
        self.assertEqual(len(changes), 0)
        self.assertEqual(len(tracking_value_ids), 0)

    def test_mail_track_lead_properties_noerror(self):
        # arrange
        person = self.env.ref("base.main_partner")
        tracked_fields = {
            "lead_properties": {"string": "Properties", "type": "properties"}
        }
        initial_values = {"3f32dd2678757113": False}

        patch_changes = {1234: "lead_properties"}
        patch_tracking_value_ids = [
            Command.create(
                {
                    "old_value_integer": 15,
                    "new_value_integer": 10,
                    "old_value_char": "Azure Interior",
                    "new_value_char": "Deco Addict",
                    "field_info": {
                        "desc": "Properties: Ev",
                        "name": "lead_properties",
                        "type": "many2one",
                    },
                }
            )
        ]

        with patch(
            "odoo.addons.mail.models.models.Base._mail_track",
            return_value=(patch_changes, patch_tracking_value_ids),
        ):
            # act
            person._mail_track(tracked_fields, initial_values)

    def test_tm_post_message_keep_all(self):
        partner = self.env.ref("base.main_partner")

        data = {
            "res.partner": {partner.id: {"phone": [{"mode": "test", "message": "msg"}]}}
        }

        fields = {
            "res.partner": {
                "phone": {"id": 1, "tracking_domain": "[('is_company', '=', True)]"}
            }
        }

        with patch(
            "odoo.addons.tracking_manager.models.models.Base._tm_post_message",
            return_value=data,
        ):
            with patch.object(
                type(self.env["base"]),
                "_tm_all_tracking_domain_fields",
                return_value=fields,
            ):
                res = self.env["base"]._tm_post_message(data)

        self.assertIn(partner.id, res["res.partner"])

    def test_tm_post_message_remove_field(self):
        partner = self.env.ref("base.main_partner")

        data = {
            "res.partner": {partner.id: {"phone": [{"mode": "test", "message": "msg"}]}}
        }

        fields = {
            "res.partner": {
                "phone": {"id": 1, "tracking_domain": "[('is_company', '=', False)]"}
            }
        }

        with patch(
            "odoo.addons.tracking_manager.models.models.Base._tm_post_message",
            return_value={"res.partner": {}},
        ):
            with patch.object(
                type(self.env["base"]),
                "_tm_all_tracking_domain_fields",
                return_value=fields,
            ):
                res = self.env["base"]._tm_post_message(data)

        self.assertEqual(res, {"res.partner": {}})

    def test_tm_post_message_missing_record(self):
        data = {
            "res.partner": {999999: {"phone": [{"mode": "test", "message": "msg"}]}}
        }

        fields = {"res.partner": {"phone": {"id": 1, "tracking_domain": "[]"}}}

        with patch(
            "odoo.addons.tracking_manager.models.models.Base._tm_post_message",
            return_value={"res.partner": {}},
        ):
            with patch.object(
                type(self.env["base"]),
                "_tm_all_tracking_domain_fields",
                return_value=fields,
            ):
                res = self.env["base"]._tm_post_message(data)

        self.assertEqual(res, {"res.partner": {}})

    def test_tm_post_message_no_tracking_fields(self):
        partner = self.env.ref("base.main_partner")

        data = {
            "res.partner": {partner.id: {"phone": [{"mode": "test", "message": "msg"}]}}
        }

        fields = {"res.partner": {}}

        with patch(
            "odoo.addons.tracking_manager.models.models.Base._tm_post_message",
            return_value=data,
        ):
            with patch.object(
                type(self.env["base"]),
                "_tm_all_tracking_domain_fields",
                return_value=fields,
            ):
                res = self.env["base"]._tm_post_message(data)

        self.assertEqual(res, data)
