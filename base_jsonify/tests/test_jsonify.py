# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase
from datetime import date, datetime


class TestParser(TransactionCase):
    def setUp(self):
        super().setUp()
        # Enforces TZ to validate the serialization result of a Datetime
        self.env.user.tz = "Europe/Brussels"
        self.parser = [
            "lang",
            "comment",
            "credit_limit",
            "name",
            "color",
            (
                "child_ids:children",
                [
                    ("child_ids:children", ["name"]),
                    "email",
                    ("country_id:country", ["code", "name"]),
                    "name",
                    "id",
                ],
            ),
            ("country_id:country", ["code", "name"]),
            "active",
            ("category_id", ["name"]),
            "create_date",
            "date",
        ]
        self.partner = self.env["res.partner"].create(
            {
                "name": "Akretion",
                "country_id": self.env.ref("base.fr").id,
                "lang": "en_US",  # default
                "category_id": [(0, 0, {"name": "Inovator"})],
                "child_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Sebatien Beau",
                            "country_id": self.env.ref("base.fr").id,
                        },
                    )
                ],
                "date": fields.Date.from_string("2019-10-31"),
            }
        )
        self.env.cr.execute(
            "update res_partner set create_date=%s where id=%s",
            ("2019-10-31 14:39:49", self.partner.id),
        )
        self.partner.refresh()
        self.expected_json = {
            "lang": "en_US",
            "comment": None,
            "credit_limit": 0.0,
            "name": "Akretion",
            "color": 0,
            "country": {"code": "FR", "name": "France"},
            "active": True,
            "category_id": [{"name": "Inovator"}],
            "children": [
                {
                    "id": self.partner.child_ids.id,
                    "country": {"code": "FR", "name": "France"},
                    "children": [],
                    "name": "Sebatien Beau",
                    "email": None,
                }
            ],
            "create_date": "2019-10-31T15:39:49+01:00",
            "date": "2019-10-31",
        }

    def test_json_export_basic(self):
        json_partner = self.partner.jsonify(self.parser)
        self.assertDictEqual(json_partner[0], self.expected_json)

    def test_json_export_booleans(self):
        # Check that only boolean fields have boolean values into json
        # By default if a field is not set into Odoo, the value is always False
        # This value is not the expected one into the json
        self.partner.write({"child_ids": [(6, 0, [])], "active": False, "lang": False})
        json_partner = self.partner.jsonify(self.parser)
        self.expected_json["active"] = False
        self.expected_json["lang"] = None
        self.expected_json["children"] = []
        self.assertDictEqual(json_partner[0], self.expected_json)

    def test_json_export_date_formatters(self):
        """ Test date formatters are applied correctly """
        json_partner = self.partner.jsonify(
            self.parser,
            date_formatter=lambda _, d: d,
            datetime_formatter=lambda _, d: None,
        )
        self.assertEqual(json_partner[0]["date"], date(2019, 10, 31))
        self.assertFalse(json_partner[0].get("create_date"))

    def test_json_export_date_formatters_relational(self):
        """ Test date formatters are propagated """
        m2o_parser = [("child_ids", ["create_date"])]
        result = self.env.ref("base.res_partner_2").jsonify(
            m2o_parser, datetime_formatter=lambda _, d: d
        )
        self.assertEqual(type(result[0]["child_ids"][0]["create_date"]), datetime)
