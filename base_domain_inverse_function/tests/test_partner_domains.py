# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.osv.expression import AND, OR
from odoo.tests import TransactionCase

from ..inverse_expression import inverse_AND, inverse_OR


class TestPartnerDomains(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.partner_domains = [
            [("display_name", "ilike", "Deco")],
            [("email", "ilike", "example.com")],
            [("country_id", "=", cls.env.ref("base.us").id)],
        ]

    def test_inverse_partner_domain_and(self):
        and_domains = AND(self.partner_domains)
        partner_domains = inverse_AND(and_domains)
        # Ensure there is at least 1 result
        self.assertTrue(self.partner_model.search(and_domains))
        # Ensure result is same after inverse
        self.assertEqual(
            self.partner_model.search(and_domains),
            self.partner_model.search(AND(partner_domains)),
        )

    def test_inverse_partner_domain_or(self):
        or_domains = OR(self.partner_domains)
        partner_domains = inverse_OR(or_domains)
        # Ensure there is at least 1 result
        self.assertTrue(self.partner_model.search(or_domains))
        # Ensure result is same after inverse
        self.assertEqual(
            self.partner_model.search(or_domains),
            self.partner_model.search(OR(partner_domains)),
        )

    def test_inverse_partner_domain_or_subdomain_and(self):
        partner_domains_2 = [
            [("display_name", "ilike", "Gemini")],
            [("email", "ilike", "example.com")],
            [("country_id", "=", self.env.ref("base.us").id)],
        ]
        composed_domain = OR([AND(self.partner_domains), AND(partner_domains_2)])
        decomposed_or_domains = inverse_OR(composed_domain)
        decomposed_and_domains_1 = inverse_AND(decomposed_or_domains[0])
        decomposed_and_domains_2 = inverse_AND(decomposed_or_domains[1])
        # Ensure there is at least 1 result
        self.assertTrue(self.partner_model.search(composed_domain))
        # Ensure result is same after inverse
        self.assertEqual(
            self.partner_model.search(composed_domain),
            self.partner_model.search(
                OR([AND(decomposed_and_domains_1), AND(decomposed_and_domains_2)])
            ),
        )

    def test_inverse_partner_domain_and_subdomain_or(self):
        partner_domains_2 = [
            [("display_name", "ilike", "Gemini")],
            [("email", "ilike", "example.com")],
            [("country_id", "=", self.env.ref("base.us").id)],
        ]
        composed_domain = AND([OR(self.partner_domains), OR(partner_domains_2)])
        decomposed_and_domains = inverse_AND(composed_domain)
        decomposed_or_domains_1 = inverse_OR(decomposed_and_domains[0])
        decomposed_or_domains_2 = inverse_OR(decomposed_and_domains[1])
        # Ensure there is at least 1 result
        self.assertTrue(self.partner_model.search(composed_domain))
        # Ensure result is same after inverse
        self.assertEqual(
            self.partner_model.search(composed_domain),
            self.partner_model.search(
                AND([OR(decomposed_or_domains_1), OR(decomposed_or_domains_2)])
            ),
        )
