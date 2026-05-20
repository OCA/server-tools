# Copyright 2016 ForgeFlow S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.orm.domains import CONDITION_OPERATORS

from odoo.addons.base.tests.common import BaseCommon


class QueryGenerationCase(BaseCommon):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.ResPartner = self.env["res.partner"]
        self.TrgmIndex = self.env["trgm.index"]
        self.ResPartnerCategory = self.env["res.partner.category"]

    def test_fuzzy_where_generation(self):
        """Check the generation of the where clause."""
        # the added fuzzy search operator should be available in the allowed
        # operators
        self.assertIn("%", CONDITION_OPERATORS)

        # create new query with fuzzy search operator
        query = self.ResPartner._search(
            [("name", "%", "test")], active_test=False, bypass_access=True
        )
        from_clause = query.from_clause.code
        where_clause = query.where_clause.code

        # the trigram operator must appear escaped as %% in the SQL template
        self.assertIn('"res_partner"."name"', where_clause)
        self.assertIn("%%", where_clause)

        # test the right sql query statement creation
        # now there should be only one '%'
        complete_where = self.env.cr.mogrify(
            f"SELECT FROM {from_clause} WHERE {where_clause}",
            query.where_clause.params,
        )
        self.assertEqual(
            complete_where,
            b'SELECT FROM "res_partner" WHERE ("res_partner"."name") % \'test\'',
        )

    def test_fuzzy_where_generation_translatable(self):
        """Check the generation of the where clause for translatable fields."""
        # create new query with fuzzy search operator
        query = self.ResPartnerCategory.with_context(lang="en_US")._search(
            [("name", "%", "Goschaeftlic")], active_test=False, bypass_access=True
        )
        from_clause = query.from_clause.code
        where_clause = query.where_clause.code

        # the trigram operator must appear escaped as %% in the SQL template
        self.assertIn('"res_partner_category"."name"', where_clause)
        self.assertIn("%%", where_clause)

        complete_where = self.env.cr.mogrify(
            f"SELECT FROM {from_clause} WHERE {where_clause}",
            query.where_clause.params,
        )

        self.assertEqual(
            complete_where,
            b'SELECT FROM "res_partner_category" WHERE '
            b"(\"res_partner_category\".\"name\"->>'en_US') % 'Goschaeftlic'",
        )

    def test_fuzzy_search(self):
        """Test the fuzzy search itself."""
        if self.TrgmIndex._trgm_extension_exists() != "installed":
            return

        if not self.TrgmIndex.index_exists("res.partner", "name"):
            field_partner_name = self.env.ref("base.field_res_partner__name")
            self.TrgmIndex.create(
                {"field_id": field_partner_name.id, "index_type": "gin"}
            )

        partner1, partner2, partner3 = self.ResPartner.create(
            [{"name": "John Smith"}, {"name": "John Smizz"}, {"name": "Linus Torvalds"}]
        )

        res = self.ResPartner.search([("name", "%", "Jon Smith")])
        self.assertIn(partner1.id, res.ids)
        self.assertIn(partner2.id, res.ids)
        self.assertNotIn(partner3.id, res.ids)

        res = self.ResPartner.search([("name", "%", "Smith John")])
        self.assertIn(partner1.id, res.ids)
        self.assertIn(partner2.id, res.ids)
        self.assertNotIn(partner3.id, res.ids)

    def test_fuzzy_search_translatable(self):
        """Test the fuzzy search on a translatable field."""
        if self.TrgmIndex._trgm_extension_exists() != "installed":
            return

        if not self.TrgmIndex.index_exists("res.partner.category", "name"):
            field_category_name = self.env.ref("base.field_res_partner_category__name")
            trgm = self.TrgmIndex.create(
                {
                    "field_id": field_category_name.id,
                    "index_type": "gin",
                    "lang": "en_US",
                }
            )
            self.env.cr.execute(
                "SELECT 1 FROM pg_indexes WHERE indexname = %s",
                (trgm.index_name,),
            )
            self.assertIsNotNone(
                self.env.cr.fetchone(),
                "create() should have built the expression index",
            )

        Category = self.ResPartnerCategory.with_context(lang="en_US")
        cat1, cat2, cat3 = Category.create(
            [
                {"name": "Goschaeftlich"},
                {"name": "Goschaeftlech"},
                {"name": "Retailer"},
            ]
        )

        res = Category.search([("name", "%", "Goschaeftlic")])
        self.assertIn(cat1.id, res.ids)
        self.assertIn(cat2.id, res.ids)
        self.assertNotIn(cat3.id, res.ids)

    def test_index_exists_unknown_field(self):
        self.assertFalse(
            self.TrgmIndex.index_exists("res.partner", "this_field_does_not_exist")
        )

    def test_create_then_unlink_drops_postgres_index(self):
        # res.partner.ref is a plain (non-translatable) Char.
        if self.TrgmIndex._trgm_extension_exists() != "installed":
            return
        field = self.env.ref("base.field_res_partner__ref")
        trgm = self.TrgmIndex.create({"field_id": field.id, "index_type": "gin"})
        self.assertTrue(trgm.index_name)
        self.assertTrue(
            self.TrgmIndex.index_exists("res.partner", "ref"),
            "index_exists must report True once a trgm.index row exists",
        )
        self.env.cr.execute(
            "SELECT 1 FROM pg_indexes WHERE indexname = %s", (trgm.index_name,)
        )
        self.assertIsNotNone(
            self.env.cr.fetchone(),
            "create() should have created the Postgres index",
        )
        index_name = trgm.index_name
        trgm.unlink()
        self.env.cr.execute(
            "SELECT 1 FROM pg_indexes WHERE indexname = %s", (index_name,)
        )
        self.assertIsNone(
            self.env.cr.fetchone(),
            "unlink() should have dropped the Postgres index",
        )

    def test_get_not_used_index_collides_on_other_table(self):
        # name_gin_idx is taken by the module's demo data
        self.env.cr.execute(
            "CREATE INDEX collide_gin_idx ON res_users USING btree (login)"
        )
        try:
            taken, suggested = self.TrgmIndex.get_not_used_index(
                "collide_gin_idx", "res_partner"
            )
            self.assertFalse(taken)
            self.assertEqual(suggested, "collide_gin_idx2")
        finally:
            self.env.cr.execute("DROP INDEX IF EXISTS collide_gin_idx")

    def test_get_not_used_index_same_table_reuses(self):
        self.env.cr.execute(
            "CREATE INDEX reuse_gin_idx ON res_partner USING btree (name)"
        )
        try:
            taken, suggested = self.TrgmIndex.get_not_used_index(
                "reuse_gin_idx", "res_partner"
            )
            self.assertTrue(taken)
            self.assertEqual(suggested, "reuse_gin_idx")
        finally:
            self.env.cr.execute("DROP INDEX IF EXISTS reuse_gin_idx")
