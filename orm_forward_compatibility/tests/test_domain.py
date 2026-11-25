# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from odoo.tests.common import TransactionCase

from odoo.addons.orm_forward_compatibility import Domain


class TestDomain(TransactionCase):
    """The shim is only useful if a ``Domain`` selects the same records as the
    equivalent 18.0 list-domain, so every test searches with both and compares.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.alice = cls.partner_model.create({"name": "Alice", "ref": "shim-a"})
        cls.bob = cls.partner_model.create({"name": "Bob", "ref": "shim-b"})
        cls.carol = cls.partner_model.create({"name": "Carol", "ref": "shim-c"})
        cls.partners = cls.alice + cls.bob + cls.carol
        # Every search is scoped to the 3 partners above, so unrelated records
        # already in the database cannot make an assertion pass or fail.
        cls.scope = [("id", "in", cls.partners.ids)]

    def _search(self, domain):
        return self.partner_model.search(self.scope + list(domain))

    def test_constructor_from_leaf_arguments(self):
        self.assertEqual(Domain("name", "=", "Alice"), [("name", "=", "Alice")])
        self.assertEqual(self._search(Domain("name", "=", "Alice")), self.alice)

    def test_constructor_from_list(self):
        domain = Domain([("name", "=", "Alice"), ("ref", "=", "shim-a")])
        # A list of leaves is implicitly AND-ed, as in 18.0.
        self.assertEqual(domain, ["&", ("name", "=", "Alice"), ("ref", "=", "shim-a")])
        self.assertEqual(self._search(domain), self.alice)

    def test_constructor_from_tuple(self):
        domain = Domain((("name", "=", "Bob"),))
        self.assertEqual(self._search(domain), self.bob)

    def test_constructor_from_domain_copies(self):
        source = Domain("name", "=", "Alice")
        copy = Domain(source)
        self.assertEqual(copy, source)
        self.assertIsNot(copy, source)

    def test_constructor_true_and_false(self):
        self.assertEqual(self._search(Domain(True)), self.partners)
        self.assertEqual(self._search(Domain([])), self.partners)
        self.assertFalse(self._search(Domain(False)))

    def test_true_and_false_attributes(self):
        self.assertEqual(self._search(Domain.TRUE), self.partners)
        self.assertFalse(self._search(Domain.FALSE))

    def test_constructor_rejects_unsupported_argument(self):
        with self.assertRaises(TypeError):
            Domain("name")
        with self.assertRaises(TypeError):
            Domain("name", "=")

    def test_and_operator(self):
        domain = Domain("name", "=", "Alice") & Domain("ref", "=", "shim-a")
        self.assertEqual(self._search(domain), self.alice)
        # Both leaves must match: mismatched ref selects nothing.
        mismatch = Domain("name", "=", "Alice") & Domain("ref", "=", "shim-b")
        self.assertFalse(self._search(mismatch))

    def test_and_operator_with_plain_list(self):
        # Chained with a plain 18.0 list-domain, on either side.
        right = Domain("name", "=", "Alice") & [("ref", "=", "shim-a")]
        left = [("ref", "=", "shim-a")] & Domain("name", "=", "Alice")
        self.assertEqual(self._search(right), self.alice)
        self.assertEqual(self._search(left), self.alice)

    def test_or_operator(self):
        domain = Domain("name", "=", "Alice") | Domain("name", "=", "Bob")
        self.assertEqual(self._search(domain), self.alice + self.bob)

    def test_or_operator_with_plain_list(self):
        right = Domain("name", "=", "Alice") | [("name", "=", "Bob")]
        left = [("name", "=", "Bob")] | Domain("name", "=", "Alice")
        self.assertEqual(self._search(right), self.alice + self.bob)
        self.assertEqual(self._search(left), self.alice + self.bob)

    def test_invert_operator(self):
        domain = ~Domain("name", "=", "Alice")
        self.assertEqual(self._search(domain), self.bob + self.carol)

    def test_and_static_method(self):
        domain = Domain.AND(
            [
                Domain("name", "!=", "Alice"),
                [("name", "!=", "Bob")],
            ]
        )
        self.assertEqual(self._search(domain), self.carol)

    def test_and_static_method_on_empty_iterable(self):
        self.assertEqual(self._search(Domain.AND([])), self.partners)

    def test_or_static_method(self):
        domain = Domain.OR(
            [
                Domain("name", "=", "Alice"),
                [("name", "=", "Carol")],
            ]
        )
        self.assertEqual(self._search(domain), self.alice + self.carol)

    def test_optimize_full_returns_self(self):
        domain = Domain("name", "=", "Alice")
        self.assertIs(domain.optimize_full(self.partner_model), domain)

    def test_optimize_full_rejects_unknown_field(self):
        with self.assertRaises(ValueError):
            Domain("no_such_field", "=", 1).optimize_full(self.partner_model)

    def test_is_accepted_as_a_plain_domain(self):
        # The point of subclassing list: no conversion at the call site.
        self.assertIsInstance(Domain("name", "=", "Alice"), list)
        self.assertEqual(
            self.partner_model.search_count(self.scope + Domain("name", "=", "Alice")),
            1,
        )
