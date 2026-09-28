# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo import fields
from odoo.tests import SavepointCase


class TestFullTextSearch(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        from .models import ResPartner, ResPartnerBase, ResUsers

        cls.loader.update_registry((ResPartnerBase, ResPartner, ResUsers))

        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "Denis Oryoz",
                "email": "denis.oryoz@example.com",
                "city": "Paris",
                "street": "12 Rue de la Liberté",
            }
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "Vincent Dupont",
                "email": "vincent.dupont@example.com",
                "city": "Lille",
                "street": "3 Rue de la Paix",
            }
        )
        cls.partner_3 = cls.env["res.partner"].create(
            {
                "name": "Vincenzo D'Agostino",
                "email": "vincenzo.dagostino@example.com",
                "city": "Roma",
                "street": "5 Via della Repubblica",
            }
        )
        cls.partner_4 = cls.env["res.partner"].create(
            {
                "name": "Roman Sanchez",
                "email": "roman.sanchez@example.com",
                "city": "Marseille",
                "street": "10 Rue de la Liberté",
            }
        )

        cls.user_1 = cls.env["res.users"].create(
            {
                "login": "User yksi",
                "partner_id": cls.partner_1.id,
            }
        )
        cls.user_2 = cls.env["res.users"].create(
            {
                "login": "User kaksi",
                "signature": "Dolor sit amet",
                "partner_id": cls.partner_2.id,
            }
        )
        cls.user_3 = cls.env["res.users"].create(
            {
                "login": "User kolme",
                "partner_id": cls.partner_3.id,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_fields_definition(self):
        field = self.env["res.partner"]._fields["full_text"]
        self.assertEqual(
            field.fields,
            {
                "name": "A",
                "email": "B",
                "city": "C",
                "street": "C",
                "commercial_company_name": "D",
            },
        )

    def test_definition_lookup(self):
        field = self.env["res.partner"]._fields["full_text"]
        definition = field._fetch_definition(self.env["res.partner"])
        fields = field.get_weighted_field_from_def(definition)
        self.assertEqual(
            fields,
            {
                "name": "A",
                "email": "B",
                "city": "C",
                "street": "C",
                "commercial_company_name": "D",
            },
        )

    def test_other_definition_lookups_1(self):
        field = self.env["res.partner"]._fields["full_text"]
        self.assertEqual(
            field.get_weighted_field_from_def(
                "((((setweight(to_tsvector('english'::regconfig, "
                "(COALESCE(name, ''::character varying))::text), 'A'::\"char\") "
                "|| setweight(to_tsvector('english'::regconfig, "
                "(COALESCE(street, ''::character varying))::text), 'C'::\"char\")) "
                "|| setweight(to_tsvector('english'::regconfig, "
                "(COALESCE(city, ''::character varying))::text), 'C'::\"char\")) "
                "|| setweight(to_tsvector('english'::regconfig, "
                "(COALESCE(email, ''::character varying))::text), 'B'::\"char\")) "
                "|| setweight(to_tsvector('english'::regconfig, "
                "(COALESCE(commercial_company_name, ''::character varying))::text), "
                "'D'::\"char\"))"
            ),
            {
                "name": "A",
                "email": "B",
                "city": "C",
                "street": "C",
                "commercial_company_name": "D",
            },
        )

    def test_other_definition_lookups_2(self):
        field = self.env["res.partner"]._fields["full_text"]
        self.assertEqual(
            field.get_weighted_field_from_def(
                "((((setweight(to_tsvector('basque'::regconfig, "
                "(COALESCE(name, ''::text))::text), 'A'::\"char\") "
                "|| setweight(to_tsvector('basque'::regconfig, "
                "(COALESCE(street, ''::\"char\"))), 'C'::\"char\")) "
                "|| setweight(to_tsvector('basque'::regconfig, "
                "(COALESCE(city, ''::character varying))::character varying), "
                "'C'::\"char\")) "
                "|| setweight(to_tsvector('basque'::regconfig, "
                "COALESCE(email, '')::\"char\"), 'B')) "
            ),
            {
                "name": "A",
                "email": "B",
                "city": "C",
                "street": "C",
            },
        )

    def test_other_definition_lookups_3(self):
        field = self.env["res.partner"]._fields["full_text"]
        self.assertEqual(
            field.get_weighted_field_from_def(""),
            {},
        )

    def test_other_definition_lookups_4(self):
        field = self.env["res.partner"]._fields["full_text"]
        self.assertEqual(
            field.get_weighted_field_from_def(
                "setweight(to_tsvector('russian', COALESCE(name, '')), 'A')"
            ),
            {
                "name": "A",
            },
        )

    def test_fetch_languages(self):
        field = self.env["res.partner"]._fields["full_text"]
        languages = field._fetch_languages(self.env["res.partner"])
        self.assertIn("simple", languages)

    def test_field_language_1(self):
        field = self.env["res.partner"]._fields["full_text"]
        definition = field._fetch_definition(self.env["res.partner"])
        self.assertEqual(field.dictionary, "english")
        self.assertEqual(field.get_language_from_def(definition), "english")

    def test_fields_definition_generation(self):
        field = fields.Searchable()
        field.fields = {
            "title": "A",
            "label": "B",
        }
        field.dictionary = "yiddish"

        self.assertEqual(
            field.get_vector_def(None),
            "setweight(to_tsvector('yiddish'::regconfig, coalesce(title, '')), 'A') "
            "|| setweight(to_tsvector('yiddish'::regconfig, coalesce(label, '')), 'B')",
        )

    def test_search_1(self):
        partners = self.env["res.partner"].search([("full_text", "@@", "Denis")])
        self.assertEqual(partners, self.partner_1)

    def test_search_2(self):
        partners = self.env["res.partner"].search([("full_text", "@@", "Vinc")])
        self.assertEqual(partners, self.partner_2 | self.partner_3)

    def test_search_3(self):
        partners = self.env["res.partner"].search([("full_text", "@@", "Roma")])
        self.assertEqual(partners, self.partner_4 | self.partner_3)

    def test_search_4(self):
        partners = self.env["res.partner"].search([("full_text", "@@", '"de la"')])
        self.assertEqual(partners, self.partner_1 | self.partner_2 | self.partner_4)

    def test_search_5(self):
        partners = self.env["res.partner"].search([("full_text", "@@", '"de la" San')])
        self.assertEqual(partners, self.partner_4)

    def test_search_6(self):
        partners = self.env["res.partner"].search([("full_text", "@@", "Vinc -Dupo")])
        self.assertEqual(partners, self.partner_3)

    def test_search_7(self):
        partners = self.env["res.partner"].search(
            [("full_text", "@@", "Marseille or Denis")]
        )
        self.assertEqual(partners, self.partner_1 | self.partner_4)

    def test_search_8(self):
        partners = self.env["res.partner"].search(
            [("full_text", "@@", "roma")],
        )
        self.assertEqual(partners, self.partner_3 | self.partner_4)

    def test_search_9(self):
        partners = self.env["res.partner"].search([("full_text", "@@", "vinz'")])
        self.assertFalse(partners)

    def test_search_10(self):
        partners = self.env["res.partner"].search(
            [
                (
                    "full_text",
                    "@@",
                    "'), ''' ', ''':*')::tsquery FROM res_partner; "
                    "DELETE FROM res_partner; --",
                )
            ]
        )
        self.assertFalse(partners)
        self.assertTrue(self.env["res.partner"].search_count([]) > 0)

    def test_search_order_rank(self):
        partners = self.env["res.partner"].search(
            [("full_text", "@@", "vincen or deni or roma")]
        )
        self.assertEqual(
            partners, self.partner_1 | self.partner_2 | self.partner_3 | self.partner_4
        )
        # Partner should be ordered by rank
        self.assertEqual(
            partners.ids,
            [
                self.partner_3.id,
                self.partner_1.id,
                self.partner_4.id,
                self.partner_2.id,
            ],
        )

    def test_search_order_default(self):
        partners = self.env["res.partner"].search(
            [("full_text", "@@", "vincen or deni or roma")],
            order=self.env["res.partner"]._order,
        )
        self.assertEqual(
            partners, self.partner_1 | self.partner_2 | self.partner_3 | self.partner_4
        )
        self.assertEqual(
            partners.ids,
            [
                self.partner_1.id,
                self.partner_4.id,
                self.partner_2.id,
                self.partner_3.id,
            ],
        )

    def test_search_count(self):
        partners_count = self.env["res.partner"].search_count(
            [("full_text", "@@", "a")]
        )
        self.assertEqual(
            partners_count,
            len(self.env["res.partner"].search([("full_text", "@@", "a")])),
        )

    def test_search_computed_1(self):
        users = self.env["res.users"].search([("full_text", "@@", "kaksi")])
        self.assertEqual(users, self.user_2)

    def test_search_computed_2(self):
        users = self.env["res.users"].search([("full_text", "@@", "amet")])
        self.assertEqual(users, self.user_2)

    def test_search_computed_3(self):
        users = self.env["res.users"].search([("full_text", "@@", "Repubblica")])
        self.assertEqual(users, self.user_3)
