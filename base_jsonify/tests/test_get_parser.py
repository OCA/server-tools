# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestParser(TransactionCase):
    def test_getting_parser(self):
        expected_parser = [
            "name",
            "active",
            "credit_limit",
            "color",
            ("category_id", ["name"]),
            ("country_id", ["name", "code"]),
            (
                "child_ids",
                [
                    "name",
                    "id",
                    "email",
                    ("country_id", ["name", "code"]),
                    ("child_ids", ["name"]),
                ],
            ),
            "lang",
            "comment",
        ]

        exporter = self.env.ref("base_jsonify.ir_exp_partner")
        parser = exporter.get_json_parser()
        self.assertListEqual(parser, expected_parser)

        # modify an ir.exports_line to put an alias for a field
        self.env.ref("base_jsonify.category_id_name").write(
            {"alias": "category_id:category/name"}
        )
        expected_parser[4] = ("category_id:category", ["name"])
        parser = exporter.get_json_parser()
        self.assertEqual(parser, expected_parser)
