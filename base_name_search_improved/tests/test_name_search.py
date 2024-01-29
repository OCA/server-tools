# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class NameSearchCase(TransactionCase):
    def setUp(self):
        super(NameSearchCase, self).setUp()
        phone_field = self.env.ref("base.field_res_partner__phone")
        model_partner = self.env.ref("base.model_res_partner")
        model_partner.name_search_ids = phone_field
        model_partner.add_smart_search = True
        model_partner.use_smart_name_search = True

        # this use does not make muche sense but with base module we dont have
        # much models to use for tests
        model_partner.name_search_domain = "[('parent_id', '=', False)]"
        self.Partner = self.env["res.partner"]
        self.partner1 = self.Partner.create(
            {"name": "Luigi Verconti", "vat": "1111", "phone": "+351 555 777 333"}
        )
        self.partner2 = self.Partner.create(
            {"name": "Ken Shabby", "vat": "2222", "phone": "+351 555 333 777"}
        )
        self.partner3 = self.Partner.create(
            {
                "name": "Johann Gambolputty of Ulm",
                "vat": "3333",
                "phone": "+351 777 333 555",
                "barcode": "1111",
            }
        )

    def test_RelevanceOrderedResults(self):
        """Return results ordered by relevance"""
        res = self.Partner.name_search("555 777")
        self.assertEqual(
            res[0][0], self.partner1.id, "Match full string honoring spaces"
        )
        self.assertEqual(
            res[1][0], self.partner2.id, "Match words honoring order of appearance"
        )
        self.assertEqual(
            res[2][0],
            self.partner3.id,
            "Match all words, regardless of order of appearance",
        )

    def test_NameSearchMustMatchAllWords(self):
        """Must Match All Words"""
        res = self.Partner.name_search("ulm aaa 555 777")
        self.assertFalse(res)

    def test_NameSearchDifferentFields(self):
        """Must Match All Words"""
        res = self.Partner.name_search("ulm 555 777")
        self.assertEqual(len(res), 1)

    def test_NameSearchDomain(self):
        """Must not return a partner with parent"""
        res = self.Partner.name_search("Edward Foster")
        self.assertFalse(res)

    def test_MustHonorDomain(self):
        """Must also honor a provided Domain"""
        res = self.Partner.name_search("+351", args=[("vat", "=", "3333")])
        gambulputty = self.partner3.id
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], gambulputty)
