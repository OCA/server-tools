# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SETATTR_SOURCES, TransactionCase, tagged

# Register our patching method in Odoo's test checker
SETATTR_SOURCES["_register_hook"] = tuple(
    list(SETATTR_SOURCES.get("_register_hook", []))
    + ["/base_name_search_improved/models/ir_model.py"],
)


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

    def setUp(self):
        super().setUp()
        self.patched_models = [
            model._name
            for model in self.env.registry.values()
            if "name_search" in vars(model)
        ]
        self.model_partner = self.env.ref("base.model_res_partner")
        self.model_partner.name_search_ids = self.phone_field
        self.model_partner.add_smart_search = True
        self.model_partner.use_smart_name_search = True

        # this use does not make muche sense but with base module we dont have
        # much models to use for tests
        self.model_partner.name_search_domain = "[('parent_id', '=', False)]"

    def tearDown(self):
        for model in self.env.registry.values():
            if "name_search" in vars(model) and model._name not in self.patched_models:
                delattr(model, "name_search")

        super().tearDown()

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
