# Copyright 2026 Syed Sameed Zafar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import phonenumbers

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestPhoneAutoFormat(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_pk = cls.env.ref("base.pk")
        cls.icp = cls.env["ir.config_parameter"].sudo()
        cls.Partner = cls.env["res.partner"]

    def _expected(self, number, region, fmt="INTERNATIONAL"):
        parsed = phonenumbers.parse(number, region)
        return phonenumbers.format_number(
            parsed, getattr(phonenumbers.PhoneNumberFormat, fmt)
        )

    def _set_config(self, fmt="INTERNATIONAL", multiple="multiple"):
        self.icp.set_param("phone_autoformat.format", fmt)
        self.icp.set_param("phone_autoformat.multiple", multiple)

    def test_create_formats_phone(self):
        self._set_config()
        partner = self.Partner.create(
            {
                "name": "Test",
                "phone": "0300 1234567",
                "country_id": self.country_pk.id,
            }
        )
        self.assertEqual(partner.phone, self._expected("03001234567", "PK"))

    def test_write_formats_phone(self):
        self._set_config()
        partner = self.Partner.create(
            {"name": "Test", "country_id": self.country_pk.id}
        )
        partner.write({"phone": "03001234567"})
        self.assertEqual(partner.phone, self._expected("03001234567", "PK"))

    def test_e164_format(self):
        self._set_config(fmt="E164")
        partner = self.Partner.create(
            {
                "name": "Test",
                "phone": "0300 1234567",
                "country_id": self.country_pk.id,
            }
        )
        self.assertEqual(partner.phone, self._expected("03001234567", "PK", "E164"))

    def test_disabled_keeps_value(self):
        self._set_config(fmt="off")
        partner = self.Partner.create(
            {
                "name": "Test",
                "phone": "0300 1234567",
                "country_id": self.country_pk.id,
            }
        )
        self.assertEqual(partner.phone, "0300 1234567")

    def test_invalid_number_is_kept(self):
        self._set_config()
        partner = self.Partner.create(
            {"name": "Test", "phone": "abc", "country_id": self.country_pk.id}
        )
        self.assertEqual(partner.phone, "abc")

    def test_multiple_numbers(self):
        self._set_config(multiple="multiple")
        partner = self.Partner.create(
            {
                "name": "Test",
                "phone": "03001234567; 03217654321",
                "country_id": self.country_pk.id,
            }
        )
        expected = ", ".join(
            [
                self._expected("03001234567", "PK"),
                self._expected("03217654321", "PK"),
            ]
        )
        self.assertEqual(partner.phone, expected)

    def test_single_number_mode_does_not_split(self):
        self._set_config(multiple="single")
        value = self.Partner._autoformat_value(
            "03001234567, 03217654321", self.country_pk
        )
        # Treated as one (invalid) number, so it is kept as typed.
        self.assertEqual(value, "03001234567, 03217654321")

    def test_phone_fields_detection(self):
        fields_ = self.Partner._autoformat_phone_fields()
        self.assertIn("phone", fields_)
        self.assertNotIn("phone_sanitized", fields_)
        self.assertNotIn("name", fields_)

    def test_onchange_formats_phone(self):
        self._set_config()
        values = {"phone": "03001234567", "country_id": self.country_pk.id}
        result = self.Partner.onchange(values, ["phone"], {"phone": {}})
        self.assertEqual(
            result.get("value", {}).get("phone"),
            self._expected("03001234567", "PK"),
        )
