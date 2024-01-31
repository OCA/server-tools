# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class NameSearchCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.phone_field = cls.env.ref("base.field_res_partner__phone")
        cls.city_field = cls.env.ref("base.field_res_partner__city")
        cls.email_field = cls.env.ref("base.field_res_partner__email")
        cls.address_field = cls.env.ref("base.field_res_partner__contact_address")
        cls.zip_field = cls.env.ref("base.field_res_partner__zip")

        cls.model_partner = cls.env.ref("base.model_res_partner")
        cls.model_partner.name_search_ids = cls.phone_field
        cls.model_partner.add_smart_search = True
        cls.model_partner.use_smart_name_search = True

        # this use does not make muche sense but with base module we dont have
        # much models to use for tests
        cls.model_partner.name_search_domain = "[('parent_id', '=', False)]"
        cls.Partner = cls.env["res.partner"]
        cls.partner1 = cls.Partner.create(
            {"name": "Luigi Verconti", "vat": "1111", "phone": "+351 555 777 333"}
        )
        cls.partner2 = cls.Partner.create(
            {"name": "Ken Shabby", "vat": "2222", "phone": "+351 555 333 777"}
        )
        cls.partner3 = cls.Partner.create(
            {
                "name": "Johann Gambolputty of Ulm",
                "vat": "3333",
                "phone": "+351 777 333 555",
                "barcode": "1111",
            }
        )

    def test_RelevanceOrderedResults(self):
        """Return results ordered by relevance"""
        res = self.Partner._name_search("555 777")
        self.assertEqual(res[0], self.partner1.id, "Match full string honoring spaces")
        self.assertEqual(
            res[1], self.partner2.id, "Match words honoring order of appearance"
        )
        self.assertEqual(
            res[2],
            self.partner3.id,
            "Match all words, regardless of order of appearance",
        )

    def test_NameSearchMustMatchAllWords(self):
        """Must Match All Words"""
        res = self.Partner._name_search("ulm aaa 555 777")
        self.assertFalse(res)

    def test_NameSearchDifferentFields(self):
        """Must Match All Words"""
        res = self.Partner._name_search("ulm 555 777")
        self.assertEqual(len(res), 1)

    def test_NameSearchDomain(self):
        """Must not return a partner with parent"""
        res = self.Partner._name_search("Edward Foster")
        self.assertFalse(res)

    def test_MustHonorDomain(self):
        """Must also honor a provided Domain"""
        res = self.Partner._name_search("+351", domain=[("vat", "=", "3333")])
        gambulputty = self.partner3.id
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], gambulputty)

    def test_SmartSearchWarning(self):
        """Must check the funtional work of _compute_smart_search_warning"""
        self.model_partner.name_search_ids = [
            (4, self.city_field.id),
            (4, self.phone_field.id),
            (4, self.email_field.id),
            (4, self.address_field.id),
        ]
        self.model_partner._compute_smart_search_warning()
        self.assertFalse(
            self.model_partner.smart_search_warning,
            "There should be no warnings",
        )

        self.model_partner.name_search_ids = [(4, self.zip_field.id)]
        self.model_partner._compute_smart_search_warning()
        self.assertIn(
            "You have selected more than 4 fields for smart search",
            self.model_partner.smart_search_warning,
            "There should be a warning as there are more than 4 fields",
        )

        translatable_field = self.env["ir.model.fields"].create(
            {
                "name": "x_translatable_field",
                "field_description": "Translatable Field",
                "ttype": "char",
                "model_id": self.model_partner.id,
                "model": self.model_partner.model,
                "translate": True,
            }
        )
        self.model_partner.name_search_ids = [(4, translatable_field.id)]
        self.model_partner._compute_smart_search_warning()
        self.assertIn(
            "You have selected translatable fields in the smart search",
            self.model_partner.smart_search_warning,
            "There should be a warning as there are translatable fields",
        )
