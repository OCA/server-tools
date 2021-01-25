# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase

from ..models.utils import convert_simple_to_full_parser


def jsonify_custom(self, field_name):
    return "yeah!"


class TestParser(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.user.tz = "Europe/Brussels"
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Akretion",
                "country_id": cls.env.ref("base.fr").id,
                "lang": "en_US",  # default
                "category_id": [(0, 0, {"name": "Inovator"})],
                "child_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Sebatien Beau",
                            "country_id": cls.env.ref("base.fr").id,
                        },
                    )
                ],
                "date": fields.Date.from_string("2019-10-31"),
            }
        )
        Langs = cls.env["res.lang"].with_context(active_test=False)
        cls.lang = Langs.search([("code", "=", "fr_FR")])
        cls.lang.active = True
        cls.env["ir.translation"]._load_module_terms(["base"], [cls.lang.code])
        category = cls.env["res.partner.category"].create({"name": "name"})
        cls.translated_target = "name_{}".format(cls.lang.code)
        cls.env["ir.translation"].create(
            {
                "type": "model",
                "name": "res.partner.category,name",
                "module": "base",
                "lang": cls.lang.code,
                "res_id": category.id,
                "value": cls.translated_target,
                "state": "translated",
            }
        )
        cls.global_resolver = cls.env["ir.exports.resolver"].create(
            {"python_code": "value['X'] = 'X'; result = value", "type": "global"}
        )
        cls.resolver = cls.env["ir.exports.resolver"].create(
            {"python_code": "result = value + '_pidgin'", "type": "field"}
        )
        cls.category_export = cls.env["ir.exports"].create(
            {
                "global_resolver_id": cls.global_resolver.id,
                "language_agnostic": True,
                "export_fields": [
                    (0, 0, {"name": "name"}),
                    (
                        0,
                        0,
                        {
                            "name": "name",
                            "target": "name:{}".format(cls.translated_target),
                            "lang_id": cls.lang.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "name",
                            "target": "name:name_resolved",
                            "resolver_id": cls.resolver.id,
                        },
                    ),
                ],
            }
        )
        cls.category = category.with_context({})
        cls.category_lang = category.with_context({"lang": cls.lang.code})

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
        expected_full_parser = convert_simple_to_full_parser(expected_parser)
        self.assertEqual(parser, expected_full_parser)

        # modify an ir.exports_line to put a target for a field
        self.env.ref("base_jsonify.category_id_name").write(
            {"target": "category_id:category/name"}
        )
        expected_parser[4] = ("category_id:category", ["name"])
        parser = exporter.get_json_parser()
        expected_full_parser = convert_simple_to_full_parser(expected_parser)
        self.assertEqual(parser, expected_full_parser)

    def test_json_export(self):
        # Enforces TZ to validate the serialization result of a Datetime
        parser = [
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
        # put our own create date to ease tests
        self.env.cr.execute(
            "update res_partner set create_date=%s where id=%s",
            ("2019-10-31 14:39:49", self.partner.id),
        )
        expected_json = {
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
        json_partner = self.partner.jsonify(parser)

        self.assertDictEqual(json_partner[0], expected_json)

        # Check that only boolean fields have boolean values into json
        # By default if a field is not set into Odoo, the value is always False
        # This value is not the expected one into the json
        self.partner.write({"child_ids": [(6, 0, [])], "active": False, "lang": False})
        json_partner = self.partner.jsonify(parser)
        expected_json["active"] = False
        expected_json["lang"] = None
        expected_json["children"] = []
        self.assertDictEqual(json_partner[0], expected_json)

    def test_one(self):
        parser = [
            "name",
        ]
        expected_json = {
            "name": "Akretion",
        }
        json_partner = self.partner.jsonify(parser, one=True)
        self.assertDictEqual(json_partner, expected_json)
        # cannot call on multiple records
        with self.assertRaises(ValueError) as err:
            self.env["res.partner"].search([]).jsonify(parser, one=True)
        self.assertIn("Expected singleton", str(err.exception))

    def test_json_export_callable_parser(self):
        self.partner.__class__.jsonify_custom = jsonify_custom
        parser = [
            # callable subparser
            ("name", lambda rec, fname: rec[fname] + " rocks!"),
            ("name:custom", "jsonify_custom"),
        ]
        expected_json = {
            "name": "Akretion rocks!",
            "custom": "yeah!",
        }
        json_partner = self.partner.jsonify(parser)
        self.assertDictEqual(json_partner[0], expected_json)
        del self.partner.__class__.jsonify_custom

    def test_full_parser(self):
        parser = self.category_export.get_json_parser()
        json = self.category.jsonify(parser)[0]
        json_fr = self.category_lang.jsonify(parser)[0]

        self.assertEqual(
            json, json_fr
        )  # starting from different languages should not change anything
        self.assertEqual(json[self.translated_target], self.translated_target)
        self.assertEqual(json["name_resolved"], "name_pidgin")  # field resolver
        self.assertEqual(json["X"], "X")  # added by global resolver

    def test_simple_parser_translations(self):
        """The simple parser result should depend on the context language."""
        parser = ["name"]
        json = self.category.jsonify(parser)[0]
        json_fr = self.category_lang.jsonify(parser)[0]

        self.assertEqual(json["name"], "name")
        self.assertEqual(json_fr["name"], self.translated_target)

    def test_simple_star_target_and_field_resolver(self):
        """The simple parser result should depend on the context language."""
        code = (
            "is_number = field_type in ('integer', 'float');"
            "ftype = 'NUMBER' if is_number else 'TEXT';"
            "value = value if is_number else str(value);"
            "result = {'Key': name, 'Value': value, 'Type': ftype, 'IsPublic': True}"
        )
        resolver = self.env["ir.exports.resolver"].create({"python_code": code})
        lang_parser = [
            {"target": "customTags=list", "name": "name", "resolver": resolver},
            {"target": "customTags=list", "name": "id", "resolver": resolver},
        ]
        parser = {"language_agnostic": True, "langs": {False: lang_parser}}
        expected_json = {
            "customTags": [
                {"Value": "name", "Key": "name", "Type": "TEXT", "IsPublic": True},
                {
                    "Value": self.category.id,
                    "Key": "id",
                    "Type": "NUMBER",
                    "IsPublic": True,
                },
            ]
        }

        json = self.category.jsonify(parser)[0]
        self.assertEqual(json, expected_json)

    def test_simple_export_with_function(self):
        self.category.__class__.jsonify_custom = jsonify_custom
        export = self.env["ir.exports"].create(
            {
                "export_fields": [
                    (0, 0, {"name": "name", "instance_method_name": "jsonify_custom"}),
                ],
            }
        )

        json = self.category.jsonify(export.get_json_parser())[0]
        self.assertEqual(json, {"name": "yeah!"})

    def test_bad_parsers(self):
        bad_field_name = ["Name"]
        with self.assertRaises(KeyError):
            self.category.jsonify(bad_field_name, one=True)

        bad_function_name = {"fields": [{"name": "name", "function": "notafunction"}]}
        with self.assertRaises(UserError):
            self.category.jsonify(bad_function_name, one=True)

        bad_subparser = {"fields": [({"name": "name"}, [{"name": "subparser_name"}])]}
        with self.assertRaises(UserError):
            self.category.jsonify(bad_subparser, one=True)
