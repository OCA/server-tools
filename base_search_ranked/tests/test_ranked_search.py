# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestRankedSearch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]

        # Create test partners
        cls.partner_demo = cls.env.ref("base.partner_demo")
        cls.partner_demo.write(
            {
                "phone": "123456789",
                "color": 1,
                "city": "Den Bosch",
            }
        )
        cls.partner_test = cls.partner_model.create(
            {
                "name": "Test Company",
                "is_company": True,
                "email": "test@company.com",
                "phone": "987654321",
                "color": 2,
            }
        )
        cls.partner_360 = cls.partner_model.create(
            {
                "name": "360 ERP BV",
                "is_company": True,
                "email": "test@company.com",
                "phone": "987654321",
                "color": 2,
                "city": "'s-Hertogenbosch",
            }
        )

    def test_ranked_search_char_field(self):
        search = {"name": {"value": "Demo", "coefficient": 50}}
        results = self.partner_model.ranked_search(search, threshold=10, limit=10)
        self.assertIn(self.partner_demo.id, results)
        self.assertGreater(results[self.partner_demo.id], 10)

    def test_ranked_search_multiple_fields(self):
        fields_searches = {
            "name": {"value": "Demo", "coefficient": 30},
            "email": {"value": "demo", "coefficient": 20},
        }
        results = self.partner_model.ranked_search(fields_searches, threshold=10)
        # Should find demo partner with higher score due to multiple matches
        self.assertGreater(results[self.partner_demo.id], 10)

    def test_ranked_search_limit(self):
        fields_searches = {"city": {"value": "genbosch", "coefficient": 50}}
        score_360 = self.partner_360.get_score(fields_searches, threshold=0)
        self.assertGreater(score_360, 1)
        score_demo = self.partner_demo.get_score(fields_searches, threshold=0)
        self.assertGreater(score_demo, 1)

        results_limited = self.partner_model.ranked_search(
            fields_searches, threshold=0, limit=1
        )
        self.assertEqual(list(results_limited), [self.partner_360.id])

        results_unlimited = self.partner_model.ranked_search(
            fields_searches, threshold=0, limit=None
        )
        self.assertIn(self.partner_360.id, results_unlimited)
        self.assertIn(self.partner_demo.id, results_unlimited)

    def test_ranked_search_empty_input_raises(self):
        with self.assertRaises(ValidationError):
            self.partner_model.ranked_search({}, threshold=0, limit=10)

    def test_ranked_search_invalid_field(self):
        fields_searches = {
            "nonexistent_field": {"value": "test", "coefficient": 10},
        }
        with self.assertRaises(ValidationError):
            self.partner_model.ranked_search(fields_searches, threshold=0, limit=10)

    def test_ranked_search_invalid_coefficient(self):
        fields_searches = {
            "name": {"value": "test", "coefficient": 150},  # > 100
        }
        with self.assertRaises(ValidationError):
            self.partner_model.ranked_search(fields_searches, threshold=0, limit=10)

        fields_searches = {
            "name": {"value": "test", "coefficient": 0},  # <= 0
        }
        with self.assertRaises(ValidationError):
            self.partner_model.ranked_search(fields_searches, threshold=0, limit=10)

    def test_ranked_search_with_domain(self):
        fields_searches = {
            "name": {"value": "Demo", "coefficient": 50},
        }

        # Search with domain that should include demo partner
        domain = [("name", "ilike", "Demo")]
        results_with_domain = self.partner_model.ranked_search(
            fields_searches, threshold=0, limit=10, domain=domain
        )

        # Search without domain
        results_without_domain = self.partner_model.ranked_search(
            fields_searches, threshold=0, limit=10
        )

        # Demo partner should be in both results
        self.assertIn(self.partner_demo.id, results_with_domain)
        self.assertIn(self.partner_demo.id, results_without_domain)

        # Results with restrictive domain should have same or fewer results
        self.assertTrue(len(results_with_domain) <= len(results_without_domain))

    def test_ranked_search_domain_filtering(self):
        fields_searches = {"name": {"value": "Test Company", "coefficient": 50}}
        domain = [("color", "!=", 2)]  # Domain excludes test company
        results_filtered = self.partner_model.ranked_search(
            fields_searches, threshold=0, limit=10, domain=domain
        )
        # Test company is not in filtered results
        self.assertNotIn(self.partner_test.id, results_filtered)

    def test_ranked_search_empty_domain(self):
        """Empty domain should work like no domain"""
        fs = {"name": {"value": "Demo", "coefficient": 50}}
        results_empty_domain = self.partner_model.ranked_search(
            fs, threshold=0, limit=10, domain=[]
        )
        results_no_domain = self.partner_model.ranked_search(
            fs, threshold=0, limit=10, domain=None
        )
        # Should return same results
        self.assertEqual(results_empty_domain, results_no_domain)

    def test_ranked_search_complex_domain(self):
        fields_searches = {
            "name": {"value": "Demo", "coefficient": 50},
        }
        domain = ["&", ("phone", "ilike", "1234"), ("color", "=", 1)]
        results = self.partner_model.ranked_search(
            fields_searches, threshold=0, limit=10, domain=domain
        )
        self.assertIn(self.partner_demo.id, results)

    def test_ranked_search_substring_matching(self):
        """Test that substring matching works properly"""
        # Test exact match
        fields_searches = {"city": {"value": "'s-Hertogenbosch", "coefficient": 50}}
        results_exact = self.partner_model.ranked_search(fields_searches, threshold=0)

        # Test substring match
        fields_searches = {"city": {"value": "bosch", "coefficient": 50}}
        results_substring = self.partner_model.ranked_search(
            fields_searches, threshold=0
        )

        # Both should find the 360 partner
        self.assertIn(self.partner_360.id, results_exact)
        self.assertIn(self.partner_360.id, results_substring)

        # Exact match should score higher than substring match
        exact_score = results_exact[self.partner_360.id]
        substring_score = results_substring[self.partner_360.id]
        self.assertGreater(exact_score, substring_score)
        self.assertGreater(substring_score, 0)  # But substring should still score > 0

    def test_scores(self):
        expected = [
            # search, value, min_score
            ("bosch", "Den Bosch", 30),
            ("bosch", "Bash", 5),
            ("genbosch", "Den Bosch", 13),
        ]
        values = [triple[1] for triple in expected]
        vals_list = [{"name": f"P{i}", "city": v} for i, v in enumerate(values)]
        partners = self.partner_model.create(vals_list)

        for i, (search, _value, min_score) in enumerate(expected):
            fs = {"city": {"value": search, "coefficient": 50}}
            partner = partners[i]
            score = partner.get_score(fs, threshold=0)
            self.assertGreaterEqual(score, min_score)
